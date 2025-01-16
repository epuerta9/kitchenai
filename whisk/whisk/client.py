from faststream import FastStream, Logger

from faststream.nats import NatsBroker
from typing import Dict, Any, Optional, List
from contextlib import asynccontextmanager
from whisk.kitchenai_sdk.kitchenai import KitchenAIApp
import time
import sys
from nats.errors import Error as NatsError
from whisk.kitchenai_sdk.nats_schema import (
    QueryRequestMessage,
    StorageRequestMessage,
    EmbedRequestMessage,
    QueryResponseMessage,
    StorageResponseMessage,
    EmbedResponseMessage,
    BroadcastRequestMessage,
    BroadcastResponseMessage,
    NatsRegisterMessage,
)

from .kitchenai_sdk.schema import QuerySchema, StorageSchema, StorageStatus, EmbedSchema


class WhiskClientError(Exception):
    """Base exception for WhiskClient errors"""

    pass


class WhiskAuthError(WhiskClientError):
    """Authentication/Authorization errors"""

    pass


class WhiskConnectionError(WhiskClientError):
    """Connection-related errors"""

    pass


class WhiskClient:
    """
    # As a client
    client = WhiskClient(user="clienta", password="...")
    await client.query("What is the temperature?", metadata={"location": "kitchen"})

    # As the KitchenAI service
    kitchenai = WhiskClient(user="kitchenai_admin", password="...", is_kitchenai=True)
    """

    def __init__(
        self,
        nats_url: str = "nats://localhost:4222",
        client_id: str = "whisk_client",
        user: str = None,
        password: str = None,
        is_kitchenai: bool = False,
        kitchen: KitchenAIApp = None,
        app: FastStream = None,
    ):
        self.client_id = client_id
        self.user = user
        self.is_kitchenai = is_kitchenai
        self.kitchen = kitchen
        self.app = app
        try:
            self.broker = NatsBroker(
                nats_url,
                name=client_id,
                user=user,
                password=password,
            )

            self.app = FastStream(
                broker=self.broker, title=f"Whisk-{client_id}", lifespan=self.lifespan
            )

            # Register subscribers immediately
            self._setup_subscribers()

        except NatsError as e:
            if "Authorization" in str(e):
                raise WhiskAuthError(
                    f"Authentication failed for user '{user}'. Please check credentials."
                ) from e
            else:
                raise WhiskConnectionError(
                    f"Failed to connect to NATS: {str(e)}"
                ) from e
        except Exception as e:
            raise WhiskClientError(f"Failed to initialize WhiskClient: {str(e)}") from e

    @asynccontextmanager
    async def lifespan(self):
        try:
            yield
        except NatsError as e:
            if "Authorization" in str(e):
                self.logger.error(f"Authorization error: {str(e)}")
                sys.exit(1)  # Exit gracefully on auth errors
            elif "permissions violation" in str(e).lower():
                self.logger.error(f"Permissions error: {str(e)}")
                # Continue running but log the error
            else:
                self.logger.error(f"NATS error: {str(e)}")
        except Exception as e:
            self.logger.error(f"Unexpected error: {str(e)}")
        finally:
            if hasattr(self, "broker"):
                await self.broker.close()

    def _setup_subscribers(self):
        # Update topic pattern to include client name
        client_prefix = (
            f"kitchenai.service.{self.client_id}"
            if not self.is_kitchenai
            else "kitchenai.service"
        )

        if self.user == "playground":
            args = ()
        else:
            args = ("queue",)
        # Setup subscribers
        self.handle_query = self.broker.subscriber(f"{client_prefix}.query.*", *args)(
            self._handle_query
        )
        self.handle_query_stream = self.broker.subscriber(
            f"{client_prefix}.query.*.stream", *args
        )(self._handle_query_stream)
        self.handle_storage = self.broker.subscriber(
            f"{client_prefix}.storage.*", *args
        )(self._handle_storage)
        self.handle_embed = self.broker.subscriber(
            f"{client_prefix}.embedding.*", *args
        )(self._handle_embed)

    async def _handle_query(
        self, msg: QueryRequestMessage, logger: Logger
    ) -> QueryResponseMessage:
        logger.info(f"Query request: {msg}")
        task = self.kitchen.query.get_task(msg.label)
        if not task:
            return QueryResponseMessage(
                request_id=msg.request_id,
                timestamp=time.time(),
                client_id=msg.client_id,
                label=msg.label,
                output=None,
                retrieval_context=None,
                stream_gen=None,
                metadata=None,
                token_counts=None,
                error=f"No task found for query",
            )

        response = await task(QuerySchema(**msg.model_dump()))
        return QueryResponseMessage(
            **response.model_dump(),
            label=msg.label,
            client_id=msg.client_id,
            request_id=msg.request_id,
            timestamp=time.time(),
        )

    async def _handle_query_stream(
        self, msg: QueryRequestMessage, logger: Logger
    ) -> None:
        logger.info(f"Query stream request: {msg}")
        resp = await self.kitchen.query.get_task("stream")(
            QuerySchema(**msg.model_dump())
        )
        async for chunk in resp.stream_gen():
            await self._publish_stream(
                QueryResponseMessage(
                    request_id=msg.request_id,
                    timestamp=time.time(),
                    client_id=msg.client_id,
                    label=msg.label,
                    output=chunk,
                    metadata=msg.metadata,
                )
            )

    async def _handle_storage(self, msg: StorageRequestMessage, logger: Logger) -> None:
        """
        This is a storage request.
        Flow:
        - KitchenAI stored file in object store and publishes a message to client bento box
        - Bento box will pick up the message and fetch the file from object store
        - Bento box service will process the file with the storage task
        - Bento box service will send a response back to the client for progress
        - KitchenAI will update object status.


        These objects are relatively short lived. They provide a more reliable means of storing files and retries.
        """
        logger.info(f"Storage request: {msg}")

        try:
            # Get the task handler
            task = self.kitchen.storage.get_task(msg.label)
            if not task:
                payload = StorageResponseMessage(
                    request_id=msg.request_id,
                    timestamp=time.time(),
                    error="No task found for storage request",
                )
                await self.broker.publish(
                    payload,
                    f"kitchenai.service.{msg.client_id}.storage.{msg.label}.response",
                )
                return
            # Get file from object store
            bucket_name = f"playground_{msg.client_id}_storage"
            bucket = await self.broker.object_storage(bucket_name)
            file_data = await bucket.get(msg.name)

            #Send an ack to the server so that it can delete the file from object store
            #Only used in playground for convenience. By default, files older than 1 hour are deleted
            await self.broker.publish(
                StorageResponseMessage(
                    request_id=msg.request_id,
                    timestamp=time.time(),
                    label=msg.label,
                    client_id=msg.client_id,
                    metadata={"file_name": msg.name},
                    status=StorageStatus.ACK,
                ),
                f"kitchenai.service.{msg.client_id}.storage.{msg.label}.response.playground",
            )

            # Process file with kitchen task
            response = await task(
                StorageSchema(id=msg.id, name=msg.name, label=msg.label, data=file_data.data, metadata=msg.metadata)
            )

            await self.broker.publish(
                StorageResponseMessage(
                    request_id=msg.request_id,
                    timestamp=time.time(),
                    label=msg.label,
                    client_id=msg.client_id,
                    metadata=response.metadata,
                    status=StorageStatus.COMPLETE,
                    token_counts=response.token_counts,
                ),
                f"kitchenai.service.{msg.client_id}.storage.{msg.label}.response",
            )

        except Exception as e:
            logger.error(f"Error processing storage request: {str(e)}")
            await self.broker.publish(
                StorageResponseMessage(
                    request_id=msg.request_id,
                    timestamp=time.time(),
                    error=str(e),
                    label=msg.label,
                    client_id=msg.client_id,
                    status=StorageStatus.ERROR,
                ),
                f"kitchenai.service.{msg.client_id}.storage.{msg.label}.response",
            )

    async def _handle_embed(self, msg: EmbedRequestMessage, logger: Logger) -> None:
        """
        This is an embed request.
        Flow:
        - KitchenAI stored file in object store and publishes a message to client bento box
        - Bento box will pick up the message and fetch the file from object store
        - Bento box service will process the file with the embed task
        - Bento box service will send a response back to the client for progress
        - KitchenAI will update the embed object status.

        These objects are relatively short lived. They provide a more reliable means of storing files and retries.
        """
        logger.info(f"Embed request: {msg}")
        try:
            # Get the task handler
            task = self.kitchen.embeddings.get_task(msg.label)
            if not task:
                return EmbedResponseMessage(
                    request_id=msg.request_id,
                    timestamp=time.time(),
                    metadata=msg.metadata,
                    label=msg.label,
                    client_id=msg.client_id,
                    error="No task found for embed request",
                )
            response = await task(EmbedSchema(**msg.model_dump()))
            await self.broker.publish(
                EmbedResponseMessage(
                    **response.model_dump(),
                    request_id=msg.request_id,
                    timestamp=time.time(),
                    metadata=msg.metadata,
                    label=msg.label,
                    client_id=msg.client_id,
                ),
                f"kitchenai.service.{msg.client_id}.embed.{msg.label}.response",
            )
        except Exception as e:
            logger.error(f"Error processing embed request: {str(e)}")
            await self.broker.publish(
                EmbedResponseMessage(
                    request_id=msg.request_id,
                    timestamp=time.time(),
                    error=str(e),
                    label=msg.label,
                    client_id=msg.client_id,
                ),
                f"kitchenai.service.{msg.client_id}.embed.{msg.label}.response",
            )

    async def _publish_stream(self, message: QueryResponseMessage):
        await self.broker.publish(
            message,
            f"kitchenai.service.{message.client_id}.query.{message.label}.stream.response",
        )

    async def query(self, message: QueryRequestMessage):
        """Send a query request"""
        response = await self.broker.request(
            message,
            f"kitchenai.service.{message.client_id}.query.{message.label}",
            timeout=10,
        )
        return response

    async def query_stream(self, message: QueryRequestMessage):
        """Send a query stream request. This will only work for KitchenAI Server
        KitchenAI will be subscribed to kitchenai.service.*.query.*.stream.response
        and will publish to SSE clients
        """
        await self.broker.publish(
            message,
            f"kitchenai.service.{message.client_id}.query.{message.label}.stream",
        )

    async def register_client(
        self, message: NatsRegisterMessage
    ) -> NatsRegisterMessage:
        """Used by the workers to register with the server"""
        ack = await self.broker.request(
            message, f"kitchenai.service.{message.client_id}.mgmt.register"
        )
        return ack

    async def store_message(self, message: StorageRequestMessage):
        """Send a storage request"""
        await self.broker.publish(
            message, f"kitchenai.service.{message.client_id}.storage.{message.label}"
        )

    async def store(self, message: StorageRequestMessage, file_data: bytes):
        """Send a storage stream request"""
        bucket_name = f"playground_{self.client_id}_storage"
        bucket = await self.broker.object_storage(bucket_name)
        await bucket.put(message.name, file_data)

        await self.store_message(message)

    async def embed(self, message: EmbedRequestMessage):
        """Send an embed request"""
        await self.broker.publish(
            message, f"kitchenai.service.{message.client_id}.embed.{message.label}"
        )

    async def broadcast(self, message: BroadcastRequestMessage):
        """Send a broadcast message"""
        await self.broker.publish(message, f"kitchenai.broadcast.{message.label}")
