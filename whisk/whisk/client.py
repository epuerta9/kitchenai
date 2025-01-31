from faststream import FastStream, Logger

from faststream.nats import NatsBroker, PullSub, JStream


from contextlib import asynccontextmanager
from whisk.kitchenai_sdk.kitchenai import KitchenAIApp
import time
import sys
from nats.errors import Error as NatsError
import logging
from whisk.kitchenai_sdk.nats_schema import (
    QueryRequestMessage,
    StorageRequestMessage,
    EmbedRequestMessage,
    QueryResponseMessage,
    StorageResponseMessage,
    EmbedResponseMessage,
    BroadcastRequestMessage,
    NatsRegisterMessage,
    StorageGetRequestMessage,
    StorageGetResponseMessage,
)
from rich.console import Console
from .kitchenai_sdk.schema import (
    WhiskQuerySchema,
    WhiskStorageSchema,
    WhiskEmbedSchema,
    NatsMessage,
    WhiskStorageStatus,
)
import httpx

console = Console()


class WhiskClientError(Exception):
    """Base exception for WhiskClient errors"""

    pass


class WhiskAuthError(WhiskClientError):
    """Authentication/Authorization errors"""

    pass


class WhiskConnectionError(WhiskClientError):
    """Connection-related errors"""

    pass


logger = logging.getLogger(__name__)


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
                nats_url, name=client_id, user=user, password=password
            )

            self.app = FastStream(
                broker=self.broker, title=f"Whisk-{client_id}", lifespan=self.lifespan
            )

            # Register subscribers immediately
            if not self.is_kitchenai:
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
                logger.error(f"Authorization error: {str(e)}")
                sys.exit(1)  # Exit gracefully on auth errors
            elif "permissions violation" in str(e).lower():
                logger.error(f"Permissions error: {str(e)}")
                # Continue running but log the error
            else:
                logger.error(f"NATS error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
        finally:
            if hasattr(self, "broker"):
                await self.broker.close()

    async def register_client(
        self, message: NatsRegisterMessage
    ) -> NatsRegisterMessage:
        """Used by the workers to register with the server"""
        ack = await self.broker.request(
            message, f"kitchenai.service.{message.client_id}.mgmt.register"
        )
        return ack

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
        self.handle_heartbeat = self.broker.subscriber(
            f"{client_prefix}.heartbeat", *args
        )(self._handle_heartbeat)

        # TODO: Uncomment this when we have streaming WIP
        # self.handle_query_stream = self.broker.subscriber(
        #     f"{client_prefix}.query.*.stream", *args
        # )(self._handle_query_stream)
        self.handle_storage = self.broker.subscriber(
            f"{client_prefix}.storage.*",
            *args,
        )(self._handle_storage)
        self.handle_storage_delete = self.broker.subscriber(
            f"{client_prefix}.storage.*.delete",
            *args,
        )(self._handle_storage_delete)

        # TODO: Uncomment this when we have embeddings WIP
        # self.handle_embed = self.broker.subscriber(
        #     f"{client_prefix}.embedding.*", *args
        # )(self._handle_embed)
        # self.handle_embed_delete = self.broker.subscriber(
        #     f"{client_prefix}.embedding.*.delete", *args
        # )(self._handle_embed_delete)

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
                messages=msg.messages,
            )

        response = await task(WhiskQuerySchema(**msg.model_dump()))
        response_dict = response.model_dump()

        # Update metadata with additional fields
        metadata = response_dict.get("metadata", {}) or {}  # Handle None case
        metadata.update(msg.metadata)
        response_dict["metadata"] = metadata
        response_dict["messages"] = msg.messages

        query_response = QueryResponseMessage(
            **response_dict,
            label=msg.label,
            client_id=msg.client_id,
            request_id=msg.request_id,
            timestamp=time.time(),
        )
        return query_response

    async def _handle_query_stream(
        self, msg: QueryRequestMessage, logger: Logger
    ) -> None:
        logger.info(f"Query stream request: {msg}")
        resp = await self.kitchen.query.get_task("stream")(
            WhiskQuerySchema(**msg.model_dump())
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

    async def _handle_heartbeat(self, msg: NatsRegisterMessage, logger: Logger) -> None:
        logger.info(f"Heartbeat request: {msg}")
        return NatsRegisterMessage(
            client_id=msg.client_id,
            version=msg.version,
            name=msg.name,
            ack=True,
            message="heartbeat",
        )

    async def _handle_storage(self, msg: StorageRequestMessage, logger: Logger) -> None:
        """
        This is a storage request.
        Flow:
        - KitchenAI will publish a message to client bento box
        - Bento box will pick up the message and request a presigned url from KitchenAI
        - KitchenAI will return a presigned url
        - Bento box will use the presigned url to download the file
        - Bento box will process the file with the storage task
        - Bento box service will send a response back to the client for progress
        - KitchenAI will update object status.
        """
        logger.info(f"Storage request: {msg}")
        # Get the task handler
        task = self.kitchen.storage.get_task(msg.label)
        if not task:
            payload = StorageResponseMessage(
                id=msg.id,
                request_id=msg.request_id,
                timestamp=time.time(),
                client_id=msg.client_id,
                label=msg.label,
                status=WhiskStorageStatus.ERROR,
                error="No task found for storage request",
            )
            logger.error(f"Error processing storage request: {payload}")
            await self.broker.publish(
                payload,
                f"kitchenai.service.{msg.client_id}.storage.{msg.label}.response",
            )
            return
        # Get file pre-signed url from kitchenai storage
        try:
            nats_response = await self.broker.request(
                StorageGetRequestMessage(
                    id=msg.id,
                    request_id=msg.request_id,
                    timestamp=time.time(),
                    label=msg.label,
                    client_id=msg.client_id,
                    presigned=True,
                ),
                f"kitchenai.service.{msg.client_id}.storage.{msg.label}.get",
            )
        except Exception as e:
            logger.error(f"Error getting presigned url: {e}")
            await self.broker.publish(
                StorageResponseMessage(
                    id=msg.id,
                    request_id=msg.request_id,
                    timestamp=time.time(),
                    error=str(e),
                    label=msg.label,
                    client_id=msg.client_id,
                    status=WhiskStorageStatus.ERROR,
                ),
                f"kitchenai.service.{msg.client_id}.storage.{msg.label}.response",
            )
            return
        presigned_message = StorageGetResponseMessage(
            id=msg.id, **NatsMessage.from_faststream(nats_response).decoded_body
        )
        if presigned_message.error:
            raise WhiskClientError(
                f"Error getting presigned url: {presigned_message.error}"
            )
        logger.info(f"Presigned url: {presigned_message.presigned_url}")
        # Use httpx to download the file using the presigned URL
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(presigned_message.presigned_url)
                if response.status_code != 200:
                    raise WhiskClientError(
                        f"Error downloading file: {response.status_code}"
                    )
                file_data = response.content
        except Exception as e:
            logger.error(f"Error downloading file: {e}")
            await self.broker.publish(
                StorageResponseMessage(
                    id=msg.id,
                    request_id=msg.request_id,
                    timestamp=time.time(),
                    error=str(e),
                    label=msg.label,
                    client_id=msg.client_id,
                    status=WhiskStorageStatus.ERROR,
                ),
                f"kitchenai.service.{msg.client_id}.storage.{msg.label}.response",
            )
            return

        # Process file with kitchen task
        try:
            response = await task(
                WhiskStorageSchema(
                    id=msg.id,
                    name=msg.name,
                    label=msg.label,
                    data=file_data,
                    metadata=msg.metadata,
                )
            )
        except Exception as e:
            logger.error(f"Error processing storage request: {e}")
            await self.broker.publish(
                StorageResponseMessage(
                    id=msg.id,
                    request_id=msg.request_id,
                    timestamp=time.time(),
                    label=msg.label,
                    client_id=msg.client_id,
                    metadata=response.metadata,
                    status=WhiskStorageStatus.ERROR,
                    token_counts=response.token_counts,
                    error=str(e),
                ),
                f"kitchenai.service.{msg.client_id}.storage.{msg.label}.response",
            )
        await self.broker.publish(
            StorageResponseMessage(
                id=msg.id,
                request_id=msg.request_id,
                timestamp=time.time(),
                label=msg.label,
                client_id=msg.client_id,
                metadata=response.metadata,
                status=WhiskStorageStatus.COMPLETE,
                token_counts=response.token_counts,
            ),
            f"kitchenai.service.{msg.client_id}.storage.{msg.label}.response",
        )

    async def _handle_storage_delete(
        self, msg: StorageRequestMessage, logger: Logger
    ) -> None:
        logger.info(f"Storage delete request: {msg}")
        task = self.kitchen.storage.get_hook(msg.label, "on_delete")
        if not task:
            logger.error(f"No task found for storage delete request: {msg.label}")
            return
        await task(WhiskStorageSchema(**msg.model_dump()))

    async def _handle_embed(self, msg: EmbedRequestMessage, logger: Logger) -> None:
        """
        This is an embed request.
        This is an object stored in kitchenai but since its just a text payload, we can serialize and send it directly.
        """
        logger.info(f"Embed request: {msg}")
        try:
            # Get the task handler
            task = self.kitchen.embeddings.get_task(msg.label)
            if not task:
                embed_response = EmbedResponseMessage(
                    id=msg.id,
                    request_id=msg.request_id,
                    timestamp=time.time(),
                    label=msg.label,
                    client_id=msg.client_id,
                    error="No task found for embed request",
                )
                await self.broker.publish(
                    embed_response,
                    f"kitchenai.service.{msg.client_id}.embedding.{msg.label}.response",
                )
                return
            response = await task(WhiskEmbedSchema(**msg.model_dump()))
            await self.broker.publish(
                EmbedResponseMessage(
                    id=msg.id,
                    request_id=msg.request_id,
                    timestamp=time.time(),
                    label=msg.label,
                    client_id=msg.client_id,
                    **response.model_dump(),
                ),
                f"kitchenai.service.{msg.client_id}.embedding.{msg.label}.response",
            )
        except Exception as e:
            logger.error(f"Error processing embed request: {str(e)}")
            await self.broker.publish(
                EmbedResponseMessage(
                    id=msg.id,
                    request_id=msg.request_id,
                    timestamp=time.time(),
                    error=str(e),
                    label=msg.label,
                    client_id=msg.client_id,
                ),
                f"kitchenai.service.{msg.client_id}.embedding.{msg.label}.response",
            )

    async def _handle_embed_delete(
        self, msg: EmbedRequestMessage, logger: Logger
    ) -> None:
        logger.info(f"Embed delete request: {msg}")
        task = self.kitchen.embeddings.get_hook(msg.label, "on_delete")
        if not task:
            logger.error(f"No task found for embed delete request: {msg.label}")
            return
        await task(WhiskEmbedSchema(**msg.model_dump()))

    async def _publish_stream(self, message: QueryResponseMessage):
        await self.broker.publish(
            message,
            f"kitchenai.service.{message.client_id}.query.{message.label}.stream.response",
        )

    async def query(self, message: QueryRequestMessage) -> NatsMessage:
        """Send a query request.
        Returns a NatsMessage object
        """
        response = await self.broker.request(
            message,
            f"kitchenai.service.{message.client_id}.query.{message.label}",
            timeout=10,
        )
        return NatsMessage.from_faststream(response)

    async def query_stream(self, message: QueryRequestMessage):
        """Send a query stream request. This will only work for KitchenAI Server
        KitchenAI will be subscribed to kitchenai.service.*.query.*.stream.response
        and will publish to SSE clients
        """
        await self.broker.publish(
            message,
            f"kitchenai.service.{message.client_id}.query.{message.label}.stream",
        )

    async def register_client(self, client_id: str) -> NatsRegisterMessage:
        """Used by the workers to register with the server. Request/Reply always returns a nats message"""
        response = await self.broker.request(
            NatsRegisterMessage(
                client_id=client_id,
                version=self.kitchen.version,
                name=self.kitchen.namespace,
                bento_box=self.kitchen.to_dict(),
                client_type=self.kitchen.client_type,
                client_description=self.kitchen.client_description,
            ),
            f"kitchenai.service.{client_id}.mgmt.register",
        )
        return NatsMessage.from_faststream(response)

    async def store_message(self, message: StorageRequestMessage):
        """Send a storage request"""
        await self.broker.publish(
            message, f"kitchenai.service.{message.client_id}.storage.{message.label}"
        )

    async def store_delete(self, message: StorageRequestMessage):
        """Send a storage delete request"""
        await self.broker.publish(
            message,
            f"kitchenai.service.{message.client_id}.storage.{message.label}.delete",
        )

    async def embed(self, message: EmbedRequestMessage):
        """Send an embed request"""
        logger.info(f"Embedding request: {message}")
        await self.broker.publish(
            message, f"kitchenai.service.{message.client_id}.embedding.{message.label}"
        )

    async def embed_delete(self, message: EmbedRequestMessage):
        """Send an embed delete request"""
        await self.broker.publish(
            message,
            f"kitchenai.service.{message.client_id}.embedding.{message.label}.delete",
        )

    async def broadcast(self, message: BroadcastRequestMessage):
        """Send a broadcast message"""
        await self.broker.publish(message, f"kitchenai.broadcast.{message.label}")

    async def run(self):
        async with self.app.broker:
            response = await self.register_client(self.client_id)
            logger.info(f"Registration response: {response.decoded_body}")

            if response.decoded_body.get("error"):
                error_msg = response.decoded_body.get("error")
                logger.error(f"Registration failed: {error_msg}")
                console.print(f"[bold red]Registration Error: {error_msg}[/bold red]")
                raise Exception(error_msg)

            # Pretty print the bento box configuration
            if self.kitchen:
                console.print("\n[bold blue]KitchenAI Configuration:[/bold blue]")
                console.print(self.kitchen.to_dict(), style="cyan")

            console.print(
                "\n[bold green]✓ Successfully registered client![/bold green]"
            )

        await self.app.run()
