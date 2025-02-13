import pytest

@pytest.mark.asyncio
async def test_storage_hooks(kitchen, storage_data):
    hook_called = False
    
    @kitchen.storage.on_store("storage")
    async def storage_hook(data):
        nonlocal hook_called
        hook_called = True
    
    hook = kitchen.storage.get_hook("storage", "on_store")
    await hook(storage_data)
    assert hook_called

@pytest.mark.asyncio
async def test_delete_hooks(kitchen, storage_data):
    hook_called = False
    
    @kitchen.storage.on_delete("storage")
    async def delete_hook(data):
        nonlocal hook_called
        hook_called = True
    
    hook = kitchen.storage.get_hook("storage", "on_delete")
    await hook(storage_data)
    assert hook_called 