

from whisk.kitchenai_sdk.kitchenai import KitchenAIApp
from whisk.kitchenai_sdk.schema import (
    WhiskQuerySchema,
    WhiskQueryBaseResponseSchema,
    WhiskStorageSchema,
    WhiskStorageResponseSchema,
    WhiskEmbedSchema,
    WhiskEmbedResponseSchema,
)

try:
    from llama_index.llms.openai import OpenAI
except ImportError:
    raise ImportError("Please install llama-index to use this example")

import logging

# Initialize LLM and embeddings
llm = OpenAI(model="gpt-3.5-turbo")

kitchen = KitchenAIApp(namespace="example_bento_box")

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


@kitchen.query.handler("stream")
async def stream_handler(data: WhiskQuerySchema) -> WhiskQueryBaseResponseSchema:
    """Query handler"""

    completions = llm.astream_complete(data.query)

    async def stream_generator():
        async for completion in completions:
            yield WhiskQueryBaseResponseSchema.from_llm_invoke(
                data.query,
                completion.delta,
            )

    return WhiskQueryBaseResponseSchema(
        input=data.query,
        stream_gen=stream_generator,
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
