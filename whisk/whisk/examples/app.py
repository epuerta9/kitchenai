

from whisk.kitchenai_sdk.kitchenai import KitchenAIApp
from whisk.kitchenai_sdk.schema import (
    QuerySchema,
    QueryBaseResponseSchema,
    StorageSchema,
    StorageResponseSchema,
    EmbedSchema,
    EmbedResponseSchema,
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
async def query_handler(data: QuerySchema) -> QueryBaseResponseSchema:
    """Query handler"""

    response = await llm.acomplete(data.query)

    print(response)

    return QueryBaseResponseSchema.from_llm_invoke(
        data.query,
        response.text,
    )


@kitchen.query.handler("stream")
async def stream_handler(data: QuerySchema) -> QueryBaseResponseSchema:
    """Query handler"""

    completions = llm.astream_complete(data.query)

    async def stream_generator():
        async for completion in completions:
            yield QueryBaseResponseSchema.from_llm_invoke(
                data.query,
                completion.delta,
            )

    return QueryBaseResponseSchema(
        input=data.query,
        stream_gen=stream_generator,
    )


@kitchen.storage.handler("storage")
async def storage_handler(data: StorageSchema) -> StorageResponseSchema:
    """Storage handler"""
    print("storage handler")
    print(data)

    return StorageResponseSchema(
        data=data.data,
        metadata=data.metadata,
    )


@kitchen.embeddings.handler("embed")
async def embed_handler(data: EmbedSchema) -> EmbedResponseSchema:
    """Embed handler"""
    print("embed handler")
    print(data)
    return EmbedResponseSchema(
        text=data.text,
        metadata=data.metadata,
    )