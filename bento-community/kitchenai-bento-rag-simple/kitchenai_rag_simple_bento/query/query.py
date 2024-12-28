from kitchenai_rag_simple_bento.kitchen import app as kitchen
from kitchenai.contrib.kitchenai_sdk.schema import QuerySchema, QueryBaseResponseSchema
import logging
from kitchenai_rag_simple_bento.kitchen import chroma_collection, llm
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.vector_stores.chroma import ChromaVectorStore

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
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    index = VectorStoreIndex.from_vector_store(
        vector_store,
    )
    query_engine = index.as_query_engine(chat_mode="best", llm=llm, verbose=True)
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
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    index = VectorStoreIndex.from_vector_store(
        vector_store,
    )
    query_engine = index.as_query_engine(streaming=True, similarity_top_k=1)
    
    streaming_response = await query_engine.aquery(data.query)


    return QueryBaseResponseSchema(stream_gen=streaming_response.response_gen)





