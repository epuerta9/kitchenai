from whisk.kitchenai_sdk.kitchenai import KitchenAIApp
from whisk.kitchenai_sdk.schema import (
    WhiskQuerySchema,
    WhiskQueryBaseResponseSchema,
    DependencyType
)
from llama_index.llms.openai import OpenAI
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb
from typing import Optional

class KitchenBuilder:
    """Builder for constructing KitchenAI apps"""
    
    def __init__(self, namespace: str):
        self.kitchen = KitchenAIApp(namespace=namespace)
        self._llm: Optional[OpenAI] = None
        self._vector_store: Optional[ChromaVectorStore] = None
    
    def with_llm(self, model: str = "gpt-3.5-turbo") -> "KitchenBuilder":
        self._llm = OpenAI(model=model)
        self.kitchen.register_dependency(DependencyType.LLM, self._llm)
        return self
    
    def with_vector_store(self, path: str = "chroma_db") -> "KitchenBuilder":
        client = chromadb.PersistentClient(path=path)
        collection = client.get_or_create_collection("quickstart")
        self._vector_store = ChromaVectorStore(chroma_collection=collection)
        self.kitchen.register_dependency(DependencyType.VECTOR_STORE, self._vector_store)
        return self
    
    def build(self) -> KitchenAIApp:
        return self.kitchen

# Create the kitchen app
kitchen = (
    KitchenBuilder("example")
    .with_llm("gpt-4")
    .with_vector_store("custom_db")
    .build()
)

@kitchen.query.handler("query", DependencyType.LLM)
async def query_handler(data: WhiskQuerySchema, llm=None) -> WhiskQueryBaseResponseSchema:
    response = await llm.acomplete(data.query)
    return WhiskQueryBaseResponseSchema.from_llm_invoke(
        data.query,
        response.text
    ) 