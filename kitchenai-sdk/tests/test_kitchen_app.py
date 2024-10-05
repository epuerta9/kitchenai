import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from kitchenai_sdk.kitchenai import KitchenAIApp  # Adjust import path as necessary

@pytest.fixture
def app():
    return FastAPI()

@pytest.fixture
def kitchen_app(app):
    return KitchenAIApp(app, namespace="test")

@pytest.fixture
def client(kitchen_app):
    return TestClient(kitchen_app._app)

def test_initialization(kitchen_app):
    assert kitchen_app._namespace == "test"
    assert isinstance(kitchen_app._app, FastAPI)
    assert kitchen_app._metadata == {}

def test_get_metadata(client):
    response = client.get("/test/meta")
    assert response.status_code == 200
    assert response.json() == {}

def test_query_decorator(kitchen_app, client):
    @kitchen_app.query("test_query")
    def test_query(request: Request):
        return {"message": "Query successful"}

    response = client.post("/test/query/test_query")
    assert response.status_code == 200
    assert response.json() == {"message": "Query successful"}
    assert "query" in kitchen_app._metadata
    assert "test_query" in kitchen_app._metadata["query"]

def test_storage_decorator(kitchen_app, client):
    @kitchen_app.storage("test_storage")
    def test_storage(request: Request):
        return {"message": "Storage successful"}

    response = client.post("/test/storage/test_storage")
    assert response.status_code == 200
    assert response.json() == {"message": "Storage successful"}
    assert "storage" in kitchen_app._metadata
    assert "test_storage" in kitchen_app._metadata["storage"]

def test_embedding_decorator(kitchen_app, client):
    @kitchen_app.embedding("test_embedding")
    def test_embedding(request: Request):
        return {"message": "Embedding successful"}

    response = client.post("/test/embedding/test_embedding")
    assert response.status_code == 200
    assert response.json() == {"message": "Embedding successful"}
    assert "embedding" in kitchen_app._metadata
    assert "test_embedding" in kitchen_app._metadata["embedding"]

def test_runnable_decorator(kitchen_app, client):
    @kitchen_app.runnable("test_runnable")
    def test_runnable(request: Request):
        return {"message": "Runnable successful"}

    response = client.post("/test/runnable/test_runnable")
    assert response.status_code == 200
    assert response.json() == {"message": "Runnable successful"}
    assert "runnable" in kitchen_app._metadata
    assert "test_runnable" in kitchen_app._metadata["runnable"]

@pytest.mark.asyncio
async def test_async_decorator(kitchen_app, client):
    @kitchen_app.query("async_query")
    async def async_query(request: Request):
        return {"message": "Async query successful"}

    response = client.post("/test/query/async_query")
    assert response.status_code == 200
    assert response.json() == {"message": "Async query successful"}

def test_multiple_decorators(kitchen_app, client):
    @kitchen_app.query("multi_query")
    @kitchen_app.storage("multi_storage")
    def multi_function(request: Request):
        return {"message": "Multiple decorators successful"}

    query_response = client.post("/test/query/multi_query")
    storage_response = client.post("/test/storage/multi_storage")

    assert query_response.status_code == 200
    assert storage_response.status_code == 200
    assert query_response.json() == storage_response.json() == {"message": "Multiple decorators successful"}

    assert "query" in kitchen_app._metadata and "multi_query" in kitchen_app._metadata["query"]
    assert "storage" in kitchen_app._metadata and "multi_storage" in kitchen_app._metadata["storage"]

def test_metadata_accumulation(kitchen_app):
    @kitchen_app.query("query1")
    def query1(request: Request):
        pass

    @kitchen_app.query("query2")
    def query2(request: Request):
        pass

    @kitchen_app.storage("storage1")
    def storage1(request: Request):
        pass

    assert len(kitchen_app._metadata["query"]) == 2
    assert len(kitchen_app._metadata["storage"]) == 1
    assert "query1" in kitchen_app._metadata["query"]
    assert "query2" in kitchen_app._metadata["query"]
    assert "storage1" in kitchen_app._metadata["storage"]

def test_custom_namespace(app):
    custom_app = KitchenAIApp(app, namespace="custom")
    
    @custom_app.query("custom_query")
    def custom_query(request: Request):
        return {"message": "Custom namespace query"}

    client = TestClient(custom_app._app)
    response = client.post("/custom/query/custom_query")
    assert response.status_code == 200
    assert response.json() == {"message": "Custom namespace query"}

# Add more tests as needed for edge cases, error handling, etc.