from django.apps import AppConfig
from llama_index.llms.litellm import LiteLLM


class KitchenaiRagSimpleBentoConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "kitchenai_rag_simple_bento"

    def ready(self):
        """Initialize KitchenAI app when Django starts"""
        
        import kitchenai_rag_simple_bento.storage.vector
        import kitchenai_rag_simple_bento.query.query
        import kitchenai_rag_simple_bento.embeddings.embeddings
        
        #TODO: add better validation for config
        from django.conf import settings
        if settings.KITCHENAI_RAG_SIMPLE_BENTO["model_type"] == "ollama":
            from llama_index.llms.ollama import OLLama
            self.llm = OLLama(model=settings.KITCHENAI_RAG_SIMPLE_BENTO["model_name"])
        elif settings.KITCHENAI_RAG_SIMPLE_BENTO["model_type"] == "litellm":
            self.llm = LiteLLM(settings.KITCHENAI_RAG_SIMPLE_BENTO["model_name"])
        else:
            raise ValueError(f"Invalid model type: {settings.KITCHENAI_RAG_SIMPLE_BENTO['model_type']}")
        
        
        if settings.KITCHENAI_RAG_SIMPLE_BENTO["vector_store"] == "chroma":
            from llama_index.vector_stores.chroma import ChromaVectorStore
            import chromadb

            self.vector_client = chromadb.PersistentClient(path="chroma_db")
            self.vector_collection = self.vector_client.get_or_create_collection("quickstart")
            self.vector_store = ChromaVectorStore(chroma_collection=self.vector_collection)

        elif settings.KITCHENAI_RAG_SIMPLE_BENTO["vector_store"] == "pgvector":
            from llama_index.vector_stores.pgvector import PGVectorStore
            import pgvector
            self.vector_client = pgvector.connect()
            self.vector_store = PGVectorStore(pgvector_collection=self.vector_collection)
        else:
            raise ValueError(f"Invalid vector store: {settings.KITCHENAI_RAG_SIMPLE_BENTO['vector_store']}")


