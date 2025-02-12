from whisk.kitchenai_sdk.kitchenai import KitchenAIApp
from whisk.kitchenai_sdk.schema import (
    WhiskQuerySchema,
    WhiskQueryBaseResponseSchema,
    DependencyType,
    TokenCountSchema
)
from llama_index.llms.openai import OpenAI
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb

class KitchenFactory:
    """Factory for creating and configuring KitchenAI apps"""
    
    @staticmethod
    def create_llm():
        return OpenAI(model="gpt-3.5-turbo")
    
    @staticmethod
    def create_vector_store():
        client = chromadb.PersistentClient(path="chroma_db")
        collection = client.get_or_create_collection("quickstart")
        return ChromaVectorStore(chroma_collection=collection)
    
    @classmethod
    def create_kitchen(cls, namespace: str = "example") -> KitchenAIApp:
        # Create app
        kitchen = KitchenAIApp(namespace=namespace)
        
        # Initialize dependencies
        llm = cls.create_llm()
        vector_store = cls.create_vector_store()
        
        # Register dependencies
        kitchen.register_dependency(DependencyType.LLM, llm)
        kitchen.register_dependency(DependencyType.VECTOR_STORE, vector_store)
        
        return kitchen

# Create the kitchen app
kitchen = KitchenFactory.create_kitchen()

# Register handlers
@kitchen.query.handler("query", DependencyType.LLM)
async def query_handler(data: WhiskQuerySchema, llm=None) -> WhiskQueryBaseResponseSchema:
    response = await llm.acomplete(data.query)
    return WhiskQueryBaseResponseSchema.from_llm_invoke(
        data.query,
        response.text
    ) 