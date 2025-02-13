import pytest
from whisk.kitchenai_sdk.kitchenai import KitchenAIApp
from whisk.kitchenai_sdk.schema import (
    WhiskQuerySchema,
    WhiskStorageSchema,
    WhiskEmbedSchema,
    DependencyType,
    TokenCountSchema
)

@pytest.fixture
def kitchen():
    return KitchenAIApp(namespace="test")

@pytest.fixture
def query_data():
    return WhiskQuerySchema(
        query="test query",
        label="query",
        metadata={"test": "metadata"}
    )

@pytest.fixture
def storage_data():
    return WhiskStorageSchema(
        id=1,
        name="test.txt",
        label="storage",
        data=b"test data",
        metadata={"test": "metadata"}
    )

@pytest.fixture
def embed_data():
    return WhiskEmbedSchema(
        label="embed",
        text="test text",
        metadata={"test": "metadata"}
    )

@pytest.fixture
def token_counts():
    return TokenCountSchema(
        embedding_tokens=100,
        llm_prompt_tokens=50,
        llm_completion_tokens=30,
        total_llm_tokens=80
    )

class MockLLM:
    async def acomplete(self, query, **kwargs):
        return type('Response', (), {'text': f"Response to: {query}"})()

@pytest.fixture
def mock_llm():
    return MockLLM()

class MockVectorStore:
    def add_documents(self, documents):
        pass
    
    def similarity_search(self, query):
        return []

@pytest.fixture
def mock_vector_store():
    return MockVectorStore() 