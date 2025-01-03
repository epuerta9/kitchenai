from typing import Any
from .types import DependencyType

class DependencyManager:
    _instances = {}

    @classmethod
    def get_instance(cls, app_name: str) -> 'DependencyManager':
        if app_name not in cls._instances:
            cls._instances[app_name] = cls(app_name)
        return cls._instances[app_name]

    def __init__(self, app_name: str, sub_manager: 'SubDependencyManager' = None):
        self.app_name = app_name
        self._dependencies = {}
        self.sub_manager = sub_manager

    def register_dependency(self, dep_type: DependencyType, instance: Any):
        self._dependencies[dep_type] = instance

    def get_dependency(self, dep_type: DependencyType) -> Any:
        # First try to get from main dependencies
        if dep_type in self._dependencies:
            return self._dependencies[dep_type]
        
        # If not found and sub_manager exists, try to get from sub_manager
        if self.sub_manager is not None:
            try:
                return self.sub_manager.get_dependency(dep_type)
            except ValueError:
                pass
                
        # If dependency not found in either place
        raise ValueError(f"Dependency {dep_type} not registered for app {self.app_name}")


class SubDependencyManager(DependencyManager):
    """An abstract base dependency manager for sub-components of a bento"""
    
    def __init__(self, app_name: str, config: dict):
        super().__init__(app_name)
        self._config = config
        self._initialize_dependencies()
    
    def _initialize_dependencies(self):
        """Initialize all dependencies based on configuration"""
        self._dependencies[DependencyType.LLM] = self._create_llm()
        self._dependencies[DependencyType.VECTOR_STORE] = self._create_vector_store()
        self._dependencies[DependencyType.EMBEDDING] = self._create_embedding_model()
        self._dependencies[DependencyType.RETRIEVER] = self._create_retriever()

    @property
    def config(self) -> dict:
        """Get the current configuration"""
        return self._config

    def _create_llm(self) -> Any:
        """Create LLM instance based on config.
        
        Returns:
            Any: An instance of a language model
            
        Raises:
            NotImplementedError: Must be implemented by subclass
        """
        raise NotImplementedError("Subclasses must implement _create_llm()")

    def _create_vector_store(self) -> Any:
        """Create vector store instance based on config.
        
        Returns:
            Any: An instance of a vector store
            
        Raises:
            NotImplementedError: Must be implemented by subclass
        """
        raise NotImplementedError("Subclasses must implement _create_vector_store()")

    def _create_embedding_model(self) -> Any:
        """Create embedding model instance based on config.
        
        Returns:
            Any: An instance of an embedding model
            
        Raises:
            NotImplementedError: Must be implemented by subclass
        """
        raise NotImplementedError("Subclasses must implement _create_embedding_model()")

    def _create_retriever(self) -> Any:
        """Create retriever instance based on config.
        
        Returns:
            Any: An instance of a retriever
            
        Raises:
            NotImplementedError: Must be implemented by subclass
        """
        raise NotImplementedError("Subclasses must implement _create_retriever()")