from kitchenai_rag_simple_bento.kitchen import app as kitchen
from kitchenai.contrib.kitchenai_sdk.schema import QuerySchema, QueryBaseResponseSchema
import logging
from llama_index.core import VectorStoreIndex, StorageContext
from django.apps import apps

logger = logging.getLogger(__name__)


@kitchen.query.handler("kitchenai-bento-rag-simple")
async def kitchenai_bento_simple_rag_vjnk(data: QuerySchema):
    """
    Query the vector database with a chat interface
    class QuerySchema(Schema):
        query: str
        stream: bool = False
        metadata: dict[str, str] | None = None
    Args:
        data: QuerySchema
    
    Response:
        QueryBaseResponseSchema:
            input: str | None = None
            output: str | None = None
            retrieval_context: list[str] | None = None
            generator: Callable | None = None
            metadata: dict[str, str] | None = None
    """
    vector_store = apps.get_app_config("kitchenai_rag_simple_bento").vector_store
    index = VectorStoreIndex.from_vector_store(
        vector_store,
    )
    query_engine = index.as_query_engine(chat_mode="best", llm=apps.get_app_config("kitchenai_rag_simple_bento").llm, verbose=True)
    response = await query_engine.aquery(data.query)
    print("metadata:", response.metadata)
    print("response:", response.source_nodes)
    return QueryBaseResponseSchema(output=response.response)


@kitchen.query.handler("kitchenai-bento-rag-simple-stream")
async def kitchenai_bento_simple_rag_stream_vjnk(data: QuerySchema):
    """
    Query the vector database with a chat interface
    class QuerySchema(Schema):
        query: str
        stream: bool = False
        metadata: dict[str, str] | None = None
    Args:
        data: QuerySchema
    
    Response:
        QueryBaseResponseSchema:
            input: str | None = None
            output: str | None = None
            retrieval_context: list[str] | None = None
            generator: Callable | None = None
            metadata: dict[str, str] | None = None
    """
    vector_store = apps.get_app_config("kitchenai_rag_simple_bento").vector_store
    index = VectorStoreIndex.from_vector_store(
        vector_store,
    )
    query_engine = index.as_query_engine(chat_mode="best", llm=apps.get_app_config("kitchenai_rag_simple_bento").llm, streaming=True)
    
    streaming_response = await query_engine.aquery(data.query)


    return QueryBaseResponseSchema(stream_gen=streaming_response.response_gen)





