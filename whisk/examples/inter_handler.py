from whisk.kitchenai_sdk.kitchenai import KitchenAIApp
from whisk.kitchenai_sdk.schema import (
    WhiskQuerySchema, 
    WhiskQueryBaseResponseSchema,
    DependencyType
)

# Create app
rag_app = KitchenAIApp(namespace="rag")

@rag_app.query.handler("answer", 
    DependencyType.LLM,
    DependencyType.VECTOR_STORE,
    DependencyType.SYSTEM_PROMPT
)
async def rag_answer(
    data: WhiskQuerySchema, 
    llm=None,
    vector_store=None,
    system_prompt=None
) -> WhiskQueryBaseResponseSchema:
    """RAG handler using core dependencies"""
    try:
        # Search for relevant documents
        docs = await vector_store.similarity_search(data.query)
        
        # Generate response with context
        response = await llm.acomplete(
            data.query,
            context=docs,
            system_prompt=system_prompt
        )
        
        return WhiskQueryBaseResponseSchema.from_llm_invoke(
            data.query,
            response.text
        )
        
    except Exception as e:
        logger.error(f"Handler error: {e}")
        raise

# Initialize
from whisk.client import WhiskClient

client = WhiskClient(
    nats_url="nats://localhost:4222",
    kitchen=rag_app
)

# Client registers itself and creates service proxies 