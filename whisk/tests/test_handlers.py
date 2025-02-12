import pytest
from whisk.kitchenai_sdk.schema import (
    WhiskQuerySchema,
    WhiskQueryBaseResponseSchema,
    WhiskStorageSchema,
    WhiskStorageResponseSchema,
    WhiskEmbedSchema,
    WhiskEmbedResponseSchema
)

@pytest.mark.asyncio
async def test_query_handler(kitchen, query_data):
    @kitchen.query.handler("query")
    async def query_handler(data):
        assert data.query == query_data.query
        assert data.metadata == query_data.metadata
        return WhiskQueryBaseResponseSchema(
            input=data.query,
            output="test response"
        )
    
    handler = kitchen.query.get_task("query")
    response = await handler(query_data)
    assert response.input == query_data.query
    assert response.output == "test response"

@pytest.mark.asyncio
async def test_storage_handler(kitchen, storage_data):
    @kitchen.storage.handler("storage")
    async def storage_handler(data):
        assert data.id == storage_data.id
        assert data.name == storage_data.name
        assert data.data == storage_data.data
        return WhiskStorageResponseSchema(
            id=data.id,
            status="complete"
        )
    
    handler = kitchen.storage.get_task("storage")
    response = await handler(storage_data)
    assert response.id == storage_data.id
    assert response.status == "complete"

@pytest.mark.asyncio
async def test_embed_handler(kitchen, embed_data):
    @kitchen.embeddings.handler("embed")
    async def embed_handler(data):
        assert data.text == embed_data.text
        assert data.metadata == embed_data.metadata
        return WhiskEmbedResponseSchema(
            metadata={"embedded": True}
        )
    
    handler = kitchen.embeddings.get_task("embed")
    response = await handler(embed_data)
    assert response.metadata["embedded"] == True 