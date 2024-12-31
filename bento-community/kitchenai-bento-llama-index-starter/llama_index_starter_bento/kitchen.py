from kitchenai.contrib.kitchenai_sdk.kitchenai import KitchenAIApp
from kitchenai.contrib.kitchenai_sdk.kitchenai import KitchenAIApp
from kitchenai.contrib.kitchenai_sdk.schema import QuerySchema, EmbedSchema
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


chroma_client = chromadb.PersistentClient(path="chroma_db")
chroma_collection = chroma_client.get_or_create_collection("quickstart")
llm = OpenAI(model="gpt-4")

app = KitchenAIApp()

