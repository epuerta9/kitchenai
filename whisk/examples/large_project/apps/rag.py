from whisk.kitchenai_sdk.kitchenai import KitchenAIApp
from whisk.kitchenai_sdk.schema import WhiskQuerySchema, WhiskQueryBaseResponseSchema

rag_app = KitchenAIApp(namespace="rag")

@rag_app.query.handler("search")
async def rag_search(data: WhiskQuerySchema, llm=None, vector_store=None):
    """RAG search handler"""
    ...

@rag_app.storage.handler("ingest")
async def rag_ingest(data: WhiskStorageSchema, vector_store=None):
    """Document ingestion handler"""
    ... 