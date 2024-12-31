# Dependency Injection in KitchenAI

KitchenAI uses a powerful dependency injection system to manage and provide access to AI components like LLMs and vector stores across your application.

## Overview

The dependency injection system consists of three main components:
1. The `BentoBaseConfig` class that creates dependencies
2. The `DependencyManager` that stores and provides access to dependencies
3. The `@with_dependencies` decorator that injects dependencies into tasks

## Configuration

Dependencies are created and registered in your Bento config class:

```python
class YourBentoConfig(BentoBaseConfig):
    def create_dependencies(self, config: dict) -> dict[DependencyType, Any]:
        """Create all dependencies at once"""
        dependencies = {
            DependencyType.LLM: self._create_llm(
                config["model_type"], 
                config["model_name"]
            ),
            DependencyType.VECTOR_STORE: self._create_vector_store(
                config["vector_store"]
            )
        }
        
        # Register each dependency with the dependency manager
        for dep_type, dep_instance in dependencies.items():
            self.dependency_manager.register_dependency(dep_type, dep_instance)
            
        return dependencies
```

## Using Dependencies in Tasks

Once dependencies are registered, you can use them in your tasks using the `@with_dependencies` decorator:

```python
@task.with_dependencies(DependencyType.LLM, DependencyType.VECTOR_STORE)
async def query_documents(self, query: str, llm, vector_store):
    # Dependencies are injected as positional arguments
    results = vector_store.similarity_search(query)
    response = await llm.agenerate(results)
    return response
```

## Initialization Flow

1. During startup:
   - Django creates your BentoConfig and initializes the DependencyManager
   - The BentoConfig creates and registers dependencies
   - Your kitchen.py gets the same DependencyManager instance
   - KitchenAIApp uses this manager for dependency injection in tasks

2. In your kitchen.py:
```python
from kitchenai.contrib.kitchenai_sdk.kitchenai import KitchenAIApp
from kitchenai.contrib.kitchenai_sdk.manager import DependencyManager

# Get the dependency manager instance for this bento app
dependency_manager = DependencyManager.get_instance("kitchenai_rag_simple_bento")

# Pass the dependency manager to KitchenAIApp
app = KitchenAIApp(namespace="kitchenai_rag_simple_bento", manager=dependency_manager)
```

## Best Practices

1. Always specify dependency types in the order they appear in your function parameters
2. Use clear parameter names that match the dependency type
3. Register all dependencies during startup in the config class
4. Use type hints in your task functions to make the code more maintainable

## Example Types

Common dependency types include:
- `DependencyType.LLM` - Language Models
- `DependencyType.VECTOR_STORE` - Vector Stores for embeddings
- `DependencyType.EMBEDDINGS` - Embedding models
- `DependencyType.RETRIEVER` - Document retrievers

## Error Handling

The system will raise appropriate errors if:
- A requested dependency type isn't registered
- Dependencies are requested in a different order than the function parameters
- The dependency manager isn't properly initialized 