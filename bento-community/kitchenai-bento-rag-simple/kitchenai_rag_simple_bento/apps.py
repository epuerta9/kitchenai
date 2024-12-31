from kitchenai.bento.bento_config import BentoBaseConfig
from kitchenai.bento.types import DependencyType
from kitchenai.bento.manager import DependencyManager
from kitchenai.core.types import EnvVars, ModelType, ModelName, VectorStore
import sys
from llama_index.llms.litellm import LiteLLM

class KitchenaiRagSimpleBentoConfig(BentoBaseConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "kitchenai_rag_simple_bento"

    def __init__(self, app_name, app_module):
        super().__init__(app_name, app_module)
        self.dependency_manager = DependencyManager.get_instance(app_name)

    def get_settings_key(self) -> str:
        """Return the settings key for this bento's configuration."""
        return "KITCHENAI_RAG_SIMPLE_BENTO"

    def create_dependencies(self, config: dict) -> dict[DependencyType, any]:
        """Create and return all required dependencies.
        
        Args:
            config: Configuration dictionary from Django settings
            
        Returns:
            Dict[DependencyType, Any]: Mapping of dependency types to instances
        """
        dependencies = {}
        
        # Create LLM dependency
        dependencies[DependencyType.LLM] = LiteLLM(ModelName.GPT4O)
        
        # Create Vector Store dependency
        dependencies[DependencyType.VECTOR_STORE] = self._create_vector_store_dependency(config)
        
        return dependencies
    
    def _create_vector_store_dependency(self, config: dict):
        from llama_index.vector_stores.chroma import ChromaVectorStore
        import chromadb

        chroma_client = chromadb.PersistentClient(path="chroma_db")
        chroma_collection = chroma_client.get_or_create_collection("quickstart")

        return ChromaVectorStore(chroma_collection)
    def on_ready(self) -> None:
        """Additional initialization after dependencies are set up."""

        
        # Import kitchen to ensure app and handlers are initialized
        from .kitchen import app
