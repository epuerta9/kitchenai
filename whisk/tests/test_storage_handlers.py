import pytest
from whisk.kitchenai_sdk.schema import WhiskStorageResponseSchema, DependencyType

@pytest.mark.asyncio
async def test_basic_storage_handler(kitchen, storage_data):
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
async def test_storage_handler_with_vector_store(kitchen, storage_data, mock_vector_store):
    kitchen.register_dependency(DependencyType.VECTOR_STORE, mock_vector_store)
    
    @kitchen.storage.handler("storage", DependencyType.VECTOR_STORE)
    async def storage_handler(data, vector_store=None):
        assert vector_store == mock_vector_store
        return WhiskStorageResponseSchema(
            id=data.id,
            status="complete"
        )
    
    handler = kitchen.storage.get_task("storage")
    response = await handler(storage_data)
    assert response.id == storage_data.id 