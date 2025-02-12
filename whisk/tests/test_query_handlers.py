import pytest
from whisk.kitchenai_sdk.schema import WhiskQueryBaseResponseSchema, DependencyType

@pytest.mark.asyncio
async def test_basic_query_handler(kitchen, query_data):
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
async def test_query_handler_with_llm(kitchen, query_data, mock_llm):
    kitchen.register_dependency(DependencyType.LLM, mock_llm)
    
    @kitchen.query.handler("query", DependencyType.LLM)
    async def query_handler(data, llm=None):
        response = await llm.acomplete(data.query)
        return WhiskQueryBaseResponseSchema.from_llm_invoke(
            data.query,
            response.text
        )
    
    handler = kitchen.query.get_task("query")
    response = await handler(query_data)
    assert response.input == query_data.query
    assert response.output == f"Response to: {query_data.query}"

@pytest.mark.asyncio
async def test_query_handler_with_token_counts(kitchen, query_data, token_counts):
    @kitchen.query.handler("query")
    async def query_handler(data):
        return WhiskQueryBaseResponseSchema(
            input=data.query,
            output="test response",
            token_counts=token_counts
        )
    
    handler = kitchen.query.get_task("query")
    response = await handler(query_data)
    assert response.token_counts == token_counts 