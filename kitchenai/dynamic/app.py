from kitchenai.contrib.kitchenai_sdk.kitchenai import KitchenAIApp
from kitchenai.contrib.kitchenai_sdk.schema import QuerySchema, QueryBaseResponseSchema, EmbedSchema, StorageSchema
from kitchenai.contrib.kitchenai_sdk.schema import TokenCountSchema, StorageResponseSchema, EmbedResponseSchema
from kitchenai_llama.storage.llama_parser import Parser
from llama_index.llms.litellm import LiteLLM
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.vector_stores.chroma import ChromaVectorStore
import os 
import chromadb
from llama_index.core.node_parser import TokenTextSplitter
from llama_index.core.extractors import (
    TitleExtractor,
    QuestionsAnsweredExtractor)
from llama_index.core import Document

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

kitchen = KitchenAIApp()

llm = LiteLLM("gpt-4o")
chroma_client = chromadb.PersistentClient(path="chroma_db")
chroma_collection = chroma_client.get_or_create_collection("quickstart")

@kitchen.query.handler("kitchenai-bento-simple-rag")
async def kitchenai_bento_simple_rag_vjnk(data: QuerySchema):
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    index = VectorStoreIndex.from_vector_store(
        vector_store,
    )
    query_engine = index.as_query_engine(chat_mode="best", llm=llm, verbose=True)
    response = await query_engine.aquery(data.query)
    return QueryBaseResponseSchema(input=data.query, output=response.response, metadata=response.metadata)

@kitchen.embeddings.handler("kitchenai-bento-simple-rag")
def simple_rag_bento_vagh(data: EmbedSchema):
    documents = [Document(text=data.text)]
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    VectorStoreIndex.from_documents(
        documents, storage_context=storage_context, show_progress=True,
            transformations=[TokenTextSplitter(), TitleExtractor(),QuestionsAnsweredExtractor()]
    )
    return EmbedResponseSchema(metadata=data.metadata)

@kitchen.storage.handler("kitchenai-bento-simple-rag")
def simple_storage(data: StorageSchema, **kwargs):
    parser = Parser(api_key=os.environ.get("LLAMA_CLOUD_API_KEY", None))
    response = parser.load(data.dir, metadata=data.metadata, **kwargs)
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    VectorStoreIndex.from_documents(
        response["documents"], storage_context=storage_context, show_progress=True,
            transformations=[TokenTextSplitter(), TitleExtractor(),QuestionsAnsweredExtractor()]
    )
    return StorageResponseSchema(metadata=data.metadata)