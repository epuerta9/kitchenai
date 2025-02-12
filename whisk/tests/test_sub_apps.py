import pytest
from whisk.kitchenai_sdk.kitchenai import KitchenAIApp
from whisk.kitchenai_sdk.schema import (
    WhiskQuerySchema,
    WhiskQueryBaseResponseSchema,
    WhiskStorageSchema,
    WhiskStorageResponseSchema,
    DependencyType
)

@pytest.fixture
def chat_app():
    app = KitchenAIApp(namespace="chat")
    
    @app.query.handler("basic")
    async def basic_chat(data: WhiskQuerySchema) -> WhiskQueryBaseResponseSchema:
        return WhiskQueryBaseResponseSchema(
            input=data.query,
            output="basic response"
        )
    
    @app.query.handler("stream")
    async def stream_chat(data: WhiskQuerySchema) -> WhiskQueryBaseResponseSchema:
        return WhiskQueryBaseResponseSchema(
            input=data.query,
            output="stream response"
        )
    
    return app

@pytest.fixture
def rag_app():
    app = KitchenAIApp(namespace="rag")
    
    @app.query.handler("search")
    async def rag_search(data: WhiskQuerySchema) -> WhiskQueryBaseResponseSchema:
        return WhiskQueryBaseResponseSchema(
            input=data.query,
            output="search response"
        )
    
    @app.storage.handler("ingest")
    async def rag_ingest(data: WhiskStorageSchema) -> WhiskStorageResponseSchema:
        return WhiskStorageResponseSchema(
            id=data.id,
            status="complete"
        )
    
    return app

def test_mount_app_merges_handlers(chat_app, rag_app):
    """Test that mounting apps correctly merges handlers with prefixed labels"""
    main_app = KitchenAIApp(namespace="main")
    
    # Mount the sub-apps
    main_app.mount_app("chat", chat_app)
    main_app.mount_app("rag", rag_app)
    
    # Check query handlers
    query_handlers = main_app.query.list_tasks()
    assert "chat.basic" in query_handlers
    assert "chat.stream" in query_handlers
    assert "rag.search" in query_handlers
    
    # Check storage handlers
    storage_handlers = main_app.storage.list_tasks()
    assert "rag.ingest" in storage_handlers

def test_mount_app_merges_dependencies(chat_app, rag_app):
    """Test that mounting apps correctly merges dependencies"""
    main_app = KitchenAIApp(namespace="main")
    
    # Register dependencies in sub-apps
    mock_llm = object()
    mock_store = object()
    chat_app.register_dependency(DependencyType.LLM, mock_llm)
    rag_app.register_dependency(DependencyType.VECTOR_STORE, mock_store)
    
    # Mount the sub-apps
    main_app.mount_app("chat", chat_app)
    main_app.mount_app("rag", rag_app)
    
    # Check dependencies were merged
    assert main_app.manager.has_dependency(DependencyType.LLM)
    assert main_app.manager.has_dependency(DependencyType.VECTOR_STORE)
    assert main_app.manager.get_dependency(DependencyType.LLM) is mock_llm
    assert main_app.manager.get_dependency(DependencyType.VECTOR_STORE) is mock_store

@pytest.mark.asyncio
async def test_mounted_handlers_execution(chat_app, rag_app, query_data):
    """Test that mounted handlers can be executed"""
    main_app = KitchenAIApp(namespace="main")
    main_app.mount_app("chat", chat_app)
    
    # Get and execute the mounted handler
    handler = main_app.query.get_task("chat.basic")
    response = await handler(query_data)
    
    assert response.input == query_data.query
    assert response.output == "basic response"

def test_mount_app_propagates_new_dependencies(chat_app, rag_app):
    """Test that new dependencies are propagated to mounted apps"""
    main_app = KitchenAIApp(namespace="main")
    main_app.mount_app("chat", chat_app)
    main_app.mount_app("rag", rag_app)
    
    # Register new dependency after mounting
    mock_llm = object()
    main_app.register_dependency(DependencyType.LLM, mock_llm)
    
    # Check dependency was propagated
    assert chat_app.manager.has_dependency(DependencyType.LLM)
    assert rag_app.manager.has_dependency(DependencyType.LLM)
    assert chat_app.manager.get_dependency(DependencyType.LLM) is mock_llm
    assert rag_app.manager.get_dependency(DependencyType.LLM) is mock_llm

def test_mount_app_namespace_isolation(chat_app, rag_app):
    """Test that mounted apps maintain their original namespaces"""
    main_app = KitchenAIApp(namespace="main")
    main_app.mount_app("chat", chat_app)
    main_app.mount_app("rag", rag_app)
    
    assert main_app.namespace == "main"
    assert chat_app.namespace == "chat"
    assert rag_app.namespace == "rag"

def test_to_dict_includes_mounted_handlers(chat_app, rag_app):
    """Test that to_dict includes mounted handlers"""
    main_app = KitchenAIApp(namespace="main")
    main_app.mount_app("chat", chat_app)
    main_app.mount_app("rag", rag_app)
    
    app_dict = main_app.to_dict()
    
    assert "chat.basic" in app_dict["query_handlers"]
    assert "chat.stream" in app_dict["query_handlers"]
    assert "rag.search" in app_dict["query_handlers"]
    assert "rag.ingest" in app_dict["storage_handlers"] 