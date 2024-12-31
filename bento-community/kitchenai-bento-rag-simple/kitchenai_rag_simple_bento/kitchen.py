
from kitchenai.contrib.kitchenai_sdk.kitchenai import KitchenAIApp
from kitchenai.bento.manager import DependencyManager
from kitchenai.contrib.kitchenai_sdk.schema import QuerySchema, QueryBaseResponseSchema
from llama_index.core import VectorStoreIndex, StorageContext
from kitchenai.bento.types import DependencyType

from kitchenai_llama.storage.llama_parser import Parser
from kitchenai.contrib.kitchenai_sdk.schema import StorageSchema
from llama_index.core.node_parser import TokenTextSplitter
from llama_index.core.extractors import (
    TitleExtractor,
    QuestionsAnsweredExtractor)
from llama_index.core.vector_stores.types import MetadataFilter
from llama_index.core.vector_stores.types import MetadataFilters

from llama_index.core import Document
from kitchenai.contrib.kitchenai_sdk.schema import EmbedSchema
import os
from llama_index.llms.litellm import LiteLLM
from llama_index.vector_stores.chroma import ChromaVectorStore
from kitchenai.core.types import  ModelName
import chromadb
import logging


chroma_client = chromadb.PersistentClient(path="chroma_db")
chroma_collection = chroma_client.get_or_create_collection("quickstart")

dependency_manager = DependencyManager.get_instance("kitchenai_rag_simple_bento")
dependency_manager.register_dependency(DependencyType.LLM, LiteLLM(ModelName.GPT4O))
dependency_manager.register_dependency(DependencyType.VECTOR_STORE, ChromaVectorStore(chroma_collection))

app = KitchenAIApp(namespace="kitchenai_rag_simple_bento", manager=dependency_manager)

logger = logging.getLogger(__name__)
@app.query.handler("query", DependencyType.LLM, DependencyType.VECTOR_STORE)
async def kitchenai_bento_simple_rag_vjnk(data: QuerySchema, llm, vector_store):
    """Query handler"""
    filter_list=[
            MetadataFilter(key=key, value=value)
            for key, value in (data.metadata or {}).items()
        ]

    filters = MetadataFilters(filters=filter_list)
    index = VectorStoreIndex.from_vector_store(vector_store)
    query_engine = index.as_query_engine(chat_mode="best", filters=filters, llm=llm, verbose=True)
    response = await query_engine.aquery(data.query)
    return QueryBaseResponseSchema.from_response(data, response)


@app.query.handler("query-stream", DependencyType.LLM, DependencyType.VECTOR_STORE)
async def kitchenai_bento_simple_rag_stream_vjnk(data: QuerySchema, llm, vector_store):
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
    vector_store = vector_store
    index = VectorStoreIndex.from_vector_store(
        vector_store,
    )
    query_engine = index.as_query_engine(chat_mode="best", llm=llm, streaming=True)
    
    streaming_response = await query_engine.aquery(data.query)


    return QueryBaseResponseSchema(stream_gen=streaming_response.response_gen)

@app.storage.handler("storage", DependencyType.VECTOR_STORE)
def simple_storage(data: StorageSchema, vector_store, **kwargs):
    parser = Parser(api_key=os.environ.get("LLAMA_CLOUD_API_KEY", None))
    response = parser.load(data.dir, metadata=data.metadata, **kwargs)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    VectorStoreIndex.from_documents(
        response["documents"], storage_context=storage_context, show_progress=True,
            transformations=[TokenTextSplitter(), TitleExtractor(),QuestionsAnsweredExtractor()]
    )


@app.embeddings.handler("embeddings", DependencyType.VECTOR_STORE)
def simple_rag_bento_vagh(data: EmbedSchema, vector_store):
    documents = [Document(text=data.text, metadata=data.metadata)]
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    VectorStoreIndex.from_documents(
        documents, storage_context=storage_context, show_progress=True,
            transformations=[TokenTextSplitter(), TitleExtractor(),QuestionsAnsweredExtractor()]
    )



