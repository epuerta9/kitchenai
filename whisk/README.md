# Whisk - KitchenAI Task Management SDK

[![PyPI version](https://badge.fury.io/py/whisk.svg)](https://badge.fury.io/py/whisk)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

Whisk is a powerful SDK for building AI applications with KitchenAI. It provides a clean interface for handling queries, storage, embeddings, and dependency management.

## Features

- Simple CLI interface for managing BentoML services
- Seamless integration with KitchenAI's infrastructure
- Built-in NATS messaging support
- Easy configuration management

## Configuration

Whisk can be configured either through a YAML file or environment variables.

### Using a Config File

Create a `config.yml` file:

```yaml
nats:
  url: "nats://localhost:4222"
  user: "playground"
  password: "kitchenai_playground"
client:
  id: "whisk_client"
llm:
  cloud_api_key: ""  # Set via environment variable LLAMA_CLOUD_API_KEY
chroma:
  path: "chroma_db"
```

### Using Environment Variables

Alternatively, you can configure Whisk using environment variables:

```bash
export WHISK_NATS_URL="nats://localhost:4222"
export WHISK_NATS_USER="playground"
export WHISK_NATS_PASSWORD="kitchenai_playground"
export WHISK_CLIENT_ID="whisk_client"
export LLAMA_CLOUD_API_KEY="your-key"
export WHISK_CHROMA_PATH="chroma_db"
```

## Installation

```bash
pip install kitchenai-whisk
```

## Quick Start

```python
from whisk.kitchenai_sdk.kitchenai import KitchenAIApp
from whisk.kitchenai_sdk.schema import WhiskQuerySchema, WhiskQueryBaseResponseSchema

# Initialize app
kitchen = KitchenAIApp(namespace="quickstart")

# Create a simple query handler
@kitchen.query.handler("query")
async def query_handler(data: WhiskQuerySchema) -> WhiskQueryBaseResponseSchema:
    return WhiskQueryBaseResponseSchema(
        input=data.query,
        output="Response to: " + data.query
    )
```

## Dependency Management

Whisk provides a type-based dependency injection system similar to FastAPI. Dependencies are automatically injected based on type annotations:

```python
from whisk.kitchenai_sdk.kitchenai import KitchenAIApp
from whisk.kitchenai_sdk.schema import WhiskQuerySchema, WhiskQueryBaseResponseSchema
from llama_index.llms.openai import OpenAI
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core.prompts import PromptTemplate

# Initialize app
kitchen = KitchenAIApp(namespace="rag-app")

# Initialize and register dependencies
llm = OpenAI(model="gpt-3.5-turbo")
vector_store = ChromaVectorStore(...)
system_prompt = PromptTemplate("You are a helpful assistant...")

kitchen.register_dependency(OpenAI, llm)  # Register by type
kitchen.register_dependency(ChromaVectorStore, vector_store)
kitchen.register_dependency(PromptTemplate, system_prompt)

# Dependencies are injected based on type annotations
@kitchen.query.handler("query")
async def query_handler(
    data: WhiskQuerySchema,
    llm: OpenAI,                    # Injected automatically
    vector_store: ChromaVectorStore,  # Injected automatically
    system_prompt: PromptTemplate     # Injected automatically
) -> WhiskQueryBaseResponseSchema:
    # Use dependencies directly
    response = await llm.acomplete(
        data.query,
        system_prompt=system_prompt
    )
    return WhiskQueryBaseResponseSchema.from_llm_invoke(
        data.query,
        response.text
    )

# You can also use the DependencyType enum if you prefer
from whisk.kitchenai_sdk.schema import DependencyType

@kitchen.query.handler("query")
async def another_handler(
    data: WhiskQuerySchema,
    llm: DependencyType.LLM,              # Also works with enum types
    vector_store: DependencyType.VECTOR_STORE,
    system_prompt: DependencyType.SYSTEM_PROMPT
) -> WhiskQueryBaseResponseSchema:
    # Dependencies are still injected automatically
    response = await llm.acomplete(data.query)
    return WhiskQueryBaseResponseSchema.from_llm_invoke(
        data.query,
        response.text
    )
```

### Available Dependency Types

You can inject dependencies either by their actual types or using the DependencyType enum:

```python
# Using actual types
def handler(
    llm: OpenAI,
    vector_store: ChromaVectorStore,
    embeddings: OpenAIEmbeddings,
    prompt: PromptTemplate
): ...

# Using enum types
def handler(
    llm: DependencyType.LLM,
    vector_store: DependencyType.VECTOR_STORE,
    embeddings: DependencyType.EMBEDDINGS,
    system_prompt: DependencyType.SYSTEM_PROMPT,
    retriever: DependencyType.RETRIEVER
): ...
```

### Registering Dependencies

Dependencies can be registered in several ways:

```python
# By type (recommended)
kitchen.register_dependency(OpenAI, llm)
kitchen.register_dependency(ChromaVectorStore, vector_store)

# By enum
kitchen.register_dependency(DependencyType.LLM, llm)
kitchen.register_dependency(DependencyType.VECTOR_STORE, vector_store)

# With custom keys
kitchen.register_dependency("my_llm", llm)
kitchen.register_dependency("my_store", vector_store)
```

### Best Practices

1. **Use Type Annotations**: Prefer using actual types over enum types for better IDE support
2. **Register at Startup**: Register all dependencies when initializing your app
3. **Type Safety**: Use type hints consistently for better error detection
4. **Single Responsibility**: Each handler should only request dependencies it actually needs
5. **Documentation**: Document any special dependency requirements in handler docstrings

## Handler Types

### Query Handlers

Query handlers process text queries and return responses:

```python
@kitchen.query.handler("query", DependencyType.LLM)
async def query_handler(data: WhiskQuerySchema) -> WhiskQueryBaseResponseSchema:
    """
    Args:
        data.query: The input query string
        data.metadata: Optional metadata dictionary
        data.label: Handler label
        data.stream: Whether to stream response
    """
    return WhiskQueryBaseResponseSchema(
        input=data.query,
        output="response",
        token_counts=token_counts,  # Optional
        metadata={"key": "value"}   # Optional
    )
```

### Storage Handlers

Storage handlers manage document ingestion and storage:

```python
@kitchen.storage.handler("storage", DependencyType.VECTOR_STORE)
async def storage_handler(data: WhiskStorageSchema) -> WhiskStorageResponseSchema:
    """
    Args:
        data.id: Document ID
        data.name: Document name
        data.data: Binary document data
        data.label: Handler label
        data.metadata: Optional metadata
    """
    return WhiskStorageResponseSchema(
        id=data.id,
        status="complete",
        metadata={"stored": True}  # Optional
    )
```

### Embedding Handlers

Embedding handlers process text into vector embeddings:

```python
@kitchen.embeddings.handler("embed", DependencyType.EMBEDDINGS)
async def embed_handler(data: WhiskEmbedSchema) -> WhiskEmbedResponseSchema:
    """
    Args:
        data.text: Text to embed
        data.label: Handler label
        data.metadata: Optional metadata
    """
    return WhiskEmbedResponseSchema(
        metadata={"embedded": True},
        token_counts=token_counts  # Optional
    )
```

## Running Your App

Start your Whisk app using the CLI:

```bash
# Development with auto-reload
whisk run app:kitchen --reload

# Production
whisk run app:kitchen
```

## Best Practices

1. **Dependency Organization**: Register all dependencies at startup
2. **Error Handling**: Always return proper response schemas
3. **Metadata**: Use metadata for tracking and debugging
4. **Token Counting**: Track token usage when possible
5. **Type Hints**: Use type hints for better code clarity

## Configuration

Configure your app using environment variables or config files:

```yaml
# config.yml
nats:
  url: nats://localhost:4222
  user: your-user
  password: your-password
```

For more examples and detailed documentation, visit our [documentation](https://docs.kitchenai.dev).

## Usage

```bash
whisk --help
```