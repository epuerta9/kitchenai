from whisk.kitchenai_sdk.kitchenai import KitchenAIApp
from whisk.kitchenai_sdk.schema import (
    WhiskQuerySchema,
    WhiskQueryBaseResponseSchema,
    DependencyType
)
from llama_index.llms.openai import OpenAI
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb
from typing import Dict, Any
import yaml

class ConfiguredKitchen:
    """Configuration-driven KitchenAI app setup"""
    
    def __init__(self, config_path: str):
        with open(config_path) as f:
            self.config = yaml.safe_load(f)
        
        self.kitchen = KitchenAIApp(
            namespace=self.config.get("namespace", "example")
        )
        self._setup_dependencies()
    
    def _setup_dependencies(self):
        # Setup LLM
        if "llm" in self.config:
            llm = OpenAI(**self.config["llm"])
            self.kitchen.register_dependency(DependencyType.LLM, llm)
        
        # Setup Vector Store
        if "vector_store" in self.config:
            client = chromadb.PersistentClient(**self.config["vector_store"])
            collection = client.get_or_create_collection(
                self.config["vector_store"].get("collection", "quickstart")
            )
            store = ChromaVectorStore(chroma_collection=collection)
            self.kitchen.register_dependency(DependencyType.VECTOR_STORE, store)
    
    @property
    def app(self) -> KitchenAIApp:
        return self.kitchen

# config.yml:
"""
namespace: example
llm:
  model: gpt-4
  temperature: 0.7
vector_store:
  path: chroma_db
  collection: custom_collection
"""

# Create the kitchen app
kitchen = ConfiguredKitchen("config.yml").app

@kitchen.query.handler("query", DependencyType.LLM)
async def query_handler(data: WhiskQuerySchema, llm=None) -> WhiskQueryBaseResponseSchema:
    response = await llm.acomplete(data.query)
    return WhiskQueryBaseResponseSchema.from_llm_invoke(
        data.query,
        response.text
    ) 