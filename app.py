from kitchenai.contrib.kitchenai_sdk.kitchenai import KitchenAIApp
from kitchenai.contrib.kitchenai_sdk.api import QuerySchema, EmbedSchema
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.llms.openai import OpenAI
import os 
import chromadb
from llama_index.llms.openai import OpenAI
from llama_index.core.node_parser import TokenTextSplitter
from llama_index.core.extractors import (
    TitleExtractor,
    QuestionsAnsweredExtractor)
from llama_index.core import Document
from kitchenai.contrib.kitchenai_sdk.storage.llama_parser import Parser

kitchen = KitchenAIApp()

chroma_client = chromadb.PersistentClient(path="chroma_db")
chroma_collection = chroma_client.get_or_create_collection("quickstart")
llm = OpenAI(model="gpt-4")
chroma_collection_second_collection = chroma_client.get_or_create_collection("second_collection")

@kitchen.storage("simple-vector")
def simple_vector(dir: str, metadata: dict = {}, *args, **kwargs):
    parser = Parser(api_key=os.environ.get("LLAMA_CLOUD_API_KEY", None))
    response = parser.load(dir, metadata=metadata, **kwargs)
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    VectorStoreIndex.from_documents(
        response["documents"], storage_context=storage_context, show_progress=True,
            transformations=[TokenTextSplitter(), TitleExtractor(),QuestionsAnsweredExtractor()]
    )
    return {"response": len(response["documents"])}


@kitchen.storage("simple-vector2")
def simple_vector2(dir: str, metadata: dict = {}, *args, **kwargs):
    parser = Parser(api_key=os.environ.get("LLAMA_CLOUD_API_KEY", None))
    response = parser.load(dir, metadata=metadata, **kwargs)
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection_second_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    VectorStoreIndex.from_documents(
        response["documents"], storage_context=storage_context, show_progress=True,
            transformations=[TokenTextSplitter(), TitleExtractor(),QuestionsAnsweredExtractor()]
    )
    return {"response": len(response["documents"])}

@kitchen.query("simple-query")
def simple_query(data: QuerySchema):
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    index = VectorStoreIndex.from_vector_store(
        vector_store,
    )
    query_engine = index.as_query_engine(chat_mode="best", llm=llm, verbose=True)
    response = query_engine.query(data.query)
    return {"response": response.response}

@kitchen.stream("simple-stream")
def simple_stream(data: QuerySchema):
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    index = VectorStoreIndex.from_vector_store(
        vector_store,
    )
    query_engine = index.as_query_engine(streaming=True, llm=llm, similarity_top_k=1, verbose=True)
    response = query_engine.query(data.query)

    return response.response_gen

@kitchen.query("non-ai")
def non_ai(data: QuerySchema):
    msg = "no AI is used in this function"
    return {"response": msg}