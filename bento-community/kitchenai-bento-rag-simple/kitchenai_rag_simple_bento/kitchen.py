
from kitchenai.contrib.kitchenai_sdk.kitchenai import KitchenAIApp
from kitchenai.bento.manager import DependencyManager
from kitchenai.contrib.kitchenai_sdk.schema import QuerySchema, QueryBaseResponseSchema
from llama_index.core import VectorStoreIndex, StorageContext
from django.apps import apps
from kitchenai.bento.types import DependencyType

from kitchenai_llama.storage.llama_parser import Parser
from kitchenai.contrib.kitchenai_sdk.schema import StorageSchema
from llama_index.core.node_parser import TokenTextSplitter
from llama_index.core.extractors import (
    TitleExtractor,
    QuestionsAnsweredExtractor)
from llama_index.core import Document
from kitchenai.contrib.kitchenai_sdk.schema import EmbedSchema
from django.apps import apps
import os



#dependency_manager = DependencyManager.get_instance("kitchenai_rag_simple_bento")
app = KitchenAIApp(namespace="kitchenai_rag_simple_bento", manager=None)


@app.query.handler("kitchenai-bento-rag-simple", DependencyType.LLM, DependencyType.VECTOR_STORE)
async def kitchenai_bento_simple_rag_vjnk(data: QuerySchema, llm, vector_store):
    """Query handler"""
    index = VectorStoreIndex.from_vector_store(vector_store)
    query_engine = index.as_query_engine(chat_mode="best", llm=llm, verbose=True)
    response = await query_engine.aquery(data.query)
    return QueryBaseResponseSchema(output=response.response)


@app.storage.handler("kitchenai-bento-simple-rag")
def simple_storage(data: StorageSchema, **kwargs):
    parser = Parser(api_key=os.environ.get("LLAMA_CLOUD_API_KEY", None))
    response = parser.load(data.dir, metadata=data.metadata, **kwargs)
    vector_store = apps.get_app_config("kitchenai_rag_simple_bento").vector_store
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    VectorStoreIndex.from_documents(
        response["documents"], storage_context=storage_context, show_progress=True,
            transformations=[TokenTextSplitter(), TitleExtractor(),QuestionsAnsweredExtractor()]
    )


@app.embeddings.handler("kitchenai-bento-simple-rag")
def simple_rag_bento_vagh(data: EmbedSchema):
    documents = [Document(text=data.text)]
    vector_store = apps.get_app_config("kitchenai_rag_simple_bento").vector_store
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    VectorStoreIndex.from_documents(
        documents, storage_context=storage_context, show_progress=True,
            transformations=[TokenTextSplitter(), TitleExtractor(),QuestionsAnsweredExtractor()]
    )



