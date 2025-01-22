# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "kitchenai-whisk",
#   "llama-index",
# ]
# ///

from whisk.kitchenai_sdk.kitchenai import KitchenAIApp
from whisk.kitchenai_sdk.schema import (
    WhiskQuerySchema,
    WhiskQueryBaseResponseSchema,
    WhiskStorageSchema,
    WhiskStorageResponseSchema,
    WhiskEmbedSchema,
    WhiskEmbedResponseSchema,
)

from llama_index.llms.openai import OpenAI
import logging
import asyncio
from whisk.client import WhiskClient
# Initialize LLM and embeddings
llm = OpenAI(model="gpt-3.5-turbo")

kitchen = KitchenAIApp(namespace="example_query")

# pip install llama-index
logger = logging.getLogger(__name__)


@kitchen.query.handler("query")
async def query_handler(data: WhiskQuerySchema) -> WhiskQueryBaseResponseSchema:
    """Query handler"""

    response = await llm.acomplete(data.query)

    print(response)

    return WhiskQueryBaseResponseSchema.from_llm_invoke(
        data.query,
        response.text,
    )


@kitchen.storage.handler("storage")
async def storage_handler(data: WhiskStorageSchema) -> WhiskStorageResponseSchema:
    """Storage handler"""
    print("storage handler")

    return WhiskStorageResponseSchema(
        id=data.id,
        data=data.data,
        metadata=data.metadata,
    )

@kitchen.storage.on_delete("storage")
async def storage_delete_handler(data: WhiskStorageSchema) -> None:
    """Storage delete handler"""
    print("storage delete handler")
    print(data)


@kitchen.embeddings.handler("embed")
async def embed_handler(data: WhiskEmbedSchema) -> WhiskEmbedResponseSchema:
    """Embed handler"""
    print("embed handler")
    print(data)
    return WhiskEmbedResponseSchema(
        text=data.text,
        metadata=data.metadata,
    )

@kitchen.embeddings.on_delete("embed")
async def embed_delete_handler(data: WhiskEmbedSchema) -> None:
    """Embed delete handler"""
    print("embed delete handler")
    print(data)

if __name__ == "__main__":

    client = WhiskClient(
        nats_url="nats://localhost:4222",
        client_id="whisk_client",
        user="playground",
        password="kitchenai_playground",
        kitchen=kitchen,
    )
    async def start():
        await client.run()

    try:
        asyncio.run(start())
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
