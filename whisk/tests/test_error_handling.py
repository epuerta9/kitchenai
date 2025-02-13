import pytest
from whisk.kitchenai_sdk.schema import WhiskStorageStatus, DependencyType

@pytest.mark.asyncio
async def test_query_handler_error(kitchen, query_data):
    @kitchen.query.handler("query")
    async def query_handler(data):
        raise ValueError("Test error")
    
    handler = kitchen.query.get_task("query")
    with pytest.raises(ValueError):
        await handler(query_data)

@pytest.mark.asyncio
async def test_storage_handler_error(kitchen, storage_data):
    @kitchen.storage.handler("storage")
    async def storage_handler(data):
        raise ValueError("Test error")
    
    handler = kitchen.storage.get_task("storage")
    with pytest.raises(ValueError):
        await handler(storage_data)

def test_invalid_dependency(kitchen):
    with pytest.raises(KeyError):
        kitchen.manager.get_dependency(DependencyType.LLM) 