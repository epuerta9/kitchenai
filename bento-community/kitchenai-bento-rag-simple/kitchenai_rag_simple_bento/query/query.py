from kitchenai_rag_simple_bento.kitchen import app as kitchen
from kitchenai.contrib.kitchenai_sdk.schema import QuerySchema, QueryBaseResponseSchema
from llama_index.core import VectorStoreIndex, StorageContext
from django.apps import apps
from kitchenai.bento.types import DependencyType

# Debug logging
debug_log = open("/tmp/kitchen_debug.log", "a")
debug_log.write("\n=== Query Module Load ===\n")
debug_log.write("Before handler registration\n")
debug_log.flush()

@kitchen.query.handler("kitchenai-bento-rag-simple", DependencyType.LLM, DependencyType.VECTOR_STORE)
async def kitchenai_bento_simple_rag_vjnk(data: QuerySchema, llm, vector_store):
    """Query handler"""
    debug_log.write("Handler kitchenai-bento-rag-simple called\n")
    debug_log.flush()
    
    index = VectorStoreIndex.from_vector_store(vector_store)
    query_engine = index.as_query_engine(chat_mode="best", llm=llm, verbose=True)
    response = await query_engine.aquery(data.query)
    return QueryBaseResponseSchema(output=response.response)

debug_log.write(f"After handler registration. Tasks: {kitchen.query._tasks}\n")
debug_log.write(f"App handlers: {kitchen.to_dict()}\n")
debug_log.flush()

# Export the handler
__all__ = ['kitchenai_bento_simple_rag_vjnk']





