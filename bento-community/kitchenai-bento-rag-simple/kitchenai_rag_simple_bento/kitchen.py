from kitchenai.contrib.kitchenai_sdk.kitchenai import KitchenAIApp

from llama_index.llms.litellm import LiteLLM

import os 
import chromadb



app = KitchenAIApp()

llm = LiteLLM("gpt-4o")
chroma_client = chromadb.PersistentClient(path="chroma_db")
chroma_collection = chroma_client.get_or_create_collection("quickstart")

