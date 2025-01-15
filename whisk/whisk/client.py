from faststream import FastStream, Logger

from faststream.nats import NatsBroker
from typing import Dict, Any, Optional, List
from contextlib import asynccontextmanager
from whisk.kitchenai_sdk.kitchenai import KitchenAIApp
import json
import time
import uuid
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
    BroadcastResponseMessage
)
from .kitchenai_sdk.schema import TokenCountSchema, SourceNodeSchema

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
        user: str = "clienta",
        password: str = None,
        is_kitchenai: bool = False,
        app: KitchenAIApp = None
    ):

        self.client_id = client_id
        self.user = user
        self.is_kitchenai = is_kitchenai
        self.app = app
        try:
            self.broker = NatsBroker(
                nats_url,
                name=client_id,
                user=user,
                password=password,
            )
            
            self.app = FastStream(
                broker=self.broker,
                title=f"Whisk-{client_id}",
                lifespan=self.lifespan
            )
            
            # Register subscribers immediately
            self._setup_subscribers()
            
        except NatsError as e:
            if "Authorization" in str(e):
                raise WhiskAuthError(f"Authentication failed for user '{user}'. Please check credentials.") from e
            else:
                raise WhiskConnectionError(f"Failed to connect to NATS: {str(e)}") from e
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
            if hasattr(self, 'broker'):
                await self.broker.close()

    def _setup_subscribers(self):
        # Update topic pattern to include client name
        client_prefix = f"kitchenai.service.{self.user}" if not self.is_kitchenai else "kitchenai.service"
        
        self.handle_query = self.broker.subscriber(f"{client_prefix}.query", "queue")(self._handle_query)
        self.handle_storage = self.broker.subscriber(f"{client_prefix}.storage", "queue")(self._handle_storage)
        self.handle_broadcast = self.broker.subscriber("kitchenai.broadcast.>")(self._handle_broadcast)
        self.handle_embed = self.broker.subscriber(f"{client_prefix}.embed", "queue")(self._handle_embed)

    async def _handle_query(self, msg: QueryRequestMessage, logger: Logger):
        logger.info(f"Query request: {msg}")
        if msg.stream:
            response = QueryResponseMessage(
                request_id=msg.request_id,
                timestamp=time.time(),
                input=msg.query,
                output="Processing query...",
                metadata=msg.metadata,
            token_counts=TokenCountSchema(),
            retrieval_context=[
                SourceNodeSchema(
                    text="Sample context",
                    metadata={"source": "test"},
                    score=1.0
                )
                ]
            )
        else:
            response = QueryResponseMessage(
                request_id=msg.request_id,
                timestamp=time.time(),
                input=msg.query,
                output="Processing query...",
                metadata=msg.metadata,
                token_counts=TokenCountSchema(),
                retrieval_context=[
                    SourceNodeSchema(
                        text="Sample context",
                        metadata={"source": "test"},
                        score=1.0
                    )
                ]
            )
            return response
        await self.broker.publish(
            f"kitchenai.response.{msg.request_id}", 
            response.model_dump()
        )

    async def _handle_storage(self, msg: StorageRequestMessage, logger: Logger):
        logger.info(f"Storage request: {msg}")
        # response = StorageResponseMessage(
        #     request_id=msg.request_id,
        #     timestamp=time.time(),
        #     metadata=msg.metadata,
        #     token_counts=TokenCountSchema()
        # )
        # await self.broker.publish(
        #     f"kitchenai.response.{msg.request_id}", 
        #     response.model_dump()
        # )

    async def _handle_broadcast(self, msg: BroadcastRequestMessage, logger: Logger):
        logger.info(f"Broadcast received: {msg}")
        # response = BroadcastResponseMessage(
        #     request_id=msg.request_id,
        #     timestamp=time.time(),
        #     message=msg.message,
        #     type=msg.type,
        #     metadata=msg.metadata,
        #     token_counts=TokenCountSchema()
        # )
        # await self.broker.publish(
        #     f"kitchenai.broadcast.response.{msg.request_id}",
        #     response.model_dump()
        # )

    async def _handle_embed(self, msg: EmbedRequestMessage, logger: Logger):
        logger.info(f"Embed request: {msg}")
        # response = EmbedResponseMessage(
        #     request_id=msg.request_id,
        #     timestamp=time.time(),
        #     metadata=msg.metadata,
        #     token_counts=TokenCountSchema()
        # )
        # await self.broker.publish(
        #     f"kitchenai.response.{msg.request_id}",
        #     response.model_dump()
        # )

    async def query(self, message: QueryRequestMessage, target: str):
        """Send a query request"""
        if message.stream:
            await self.broker.publish(message, f"kitchenai.service.{target}.query")
        else:
            response = await self.broker.request(message, f"kitchenai.service.{target}.query")
            return response

    async def store(self, message: StorageRequestMessage, target: str):
        """Send a storage request"""
        await self.broker.publish(message, f"kitchenai.service.{target}.storage")

    async def embed(self, message: EmbedRequestMessage, target: str):
        """Send an embed request"""
        await self.broker.publish(message, f"kitchenai.service.{target}.embed")

    async def broadcast(self, message: BroadcastRequestMessage, target: str):
        """Send a broadcast message"""
        await self.broker.publish(message, f"kitchenai.broadcast.{target}") 