import pytest
from whisk.kitchenai_sdk.schema import DependencyType
from whisk.kitchenai_sdk.base import DependencyManager

def test_dependency_registration(kitchen, mock_llm):
    kitchen.register_dependency(DependencyType.LLM, mock_llm)
    assert kitchen.manager.has_dependency(DependencyType.LLM)
    assert kitchen.manager.get_dependency(DependencyType.LLM) == mock_llm

def test_dependency_injection(kitchen, mock_llm, query_data):
    kitchen.register_dependency(DependencyType.LLM, mock_llm)
    
    @kitchen.query.handler("test", DependencyType.LLM)
    async def test_handler(data, llm=None):
        assert llm == mock_llm
        return "success"
    
    assert "test" in kitchen.query.list_tasks()

def test_missing_dependency(kitchen, query_data):
    @kitchen.query.handler("test", DependencyType.LLM)
    async def test_handler(data, llm=None):
        assert llm is None
        return "success"
    
    assert "test" in kitchen.query.list_tasks()

def test_multiple_dependencies(kitchen, mock_llm, mock_vector_store):
    kitchen.register_dependency(DependencyType.LLM, mock_llm)
    kitchen.register_dependency(DependencyType.VECTOR_STORE, mock_vector_store)
    
    @kitchen.query.handler("test", DependencyType.LLM, DependencyType.VECTOR_STORE)
    async def test_handler(data, llm=None, vector_store=None):
        assert llm == mock_llm
        assert vector_store == mock_vector_store
        return "success"
    
    assert "test" in kitchen.query.list_tasks() 