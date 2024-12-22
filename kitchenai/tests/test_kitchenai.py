

import pytest
import asyncio
from kitchenai.contrib.kitchenai_sdk.kitchenai import KitchenAIAppV2  # Replace with the correct import path


@pytest.fixture
def app():
    return KitchenAIAppV2(namespace="test_namespace")

def test_app_initialization(app):
    assert app is not None
    assert app.namespace == "test_namespace"



@pytest.mark.asyncio
async def test_query_task_registration_and_execution(app):
    # Register a query task
    @app.query.query(label="test_query")
    async def test_query_handler(query: str):
        return f"Query processed: {query}"

    # Retrieve and execute the task
    query_task = app.query_tasks.get_task("test_query")
    assert query_task is not None

    result = await query_task("test input")
    assert result == "Query processed: test input"



def test_storage_task_registration_and_execution(app):
    # Register a storage task
    @app.storage.storage(label="save_data")
    def save_data(data: dict):
        return f"Data saved: {data}"

    # Retrieve and execute the task
    storage_task = app.storage_tasks.get_task("save_data")
    assert storage_task is not None

    result = storage_task({"key": "value"})
    assert result == "Data saved: {'key': 'value'}"



def test_embed_task_registration_and_execution(app):
    # Register an embed task
    @app.embeddings.embed(label="generate_embedding")
    def generate_embedding(data: dict):
        return {"embedding": [0.1, 0.2, 0.3]}

    # Retrieve and execute the task
    embed_task = app.embed_tasks.get_task("generate_embedding")
    assert embed_task is not None

    result = embed_task({"data": "input"})
    assert result == {"embedding": [0.1, 0.2, 0.3]}



@pytest.mark.asyncio
async def test_agent_task_registration_and_execution(app):
    # Register an agent task
    @app.agent.agent(label="run_agent")
    async def run_agent(input_data: dict):
        return {"response": f"Processed {input_data}"}

    # Retrieve and execute the task
    agent_task = app.agent_tasks.get_task("run_agent")
    assert agent_task is not None

    result = await agent_task({"key": "value"})
    assert result == {"response": "Processed {'key': 'value'}"}



def test_kitchenai_app_summary(app):
    @app.query.query(label="test_query")
    async def test_query_handler(query: str):
        return f"Query processed: {query}"

    @app.storage.storage(label="save_data")
    def save_data(data: dict):
        return f"Data saved: {data}"

    @app.embeddings.embed(label="generate_embedding")
    def generate_embedding(data: dict):
        return {"embedding": [0.1, 0.2, 0.3]}

    @app.agent_tasks.agent(label="run_agent")
    async def run_agent(input_data: dict):
        return {"response": f"Processed {input_data}"}

    summary = app.to_dict()
    assert summary == {
        "namespace": "test_namespace",
        "query_tasks": ["test_namespace.test_query"],
        "storage_tasks": ["test_namespace.save_data"],
        "embed_tasks": ["test_namespace.generate_embedding"],
        "stream_tasks": ["test_namespace.stream_results"],
        "agent_tasks": ["test_namespace.run_agent"],
    }
