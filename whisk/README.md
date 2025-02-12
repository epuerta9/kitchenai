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

## Project Structure

For larger projects, it's recommended to organize your handlers into modules. Here are some recommended patterns:

### Pattern 1: Module-based Organization

```plaintext
my_whisk_app/
├── app.py              # Main app initialization
├── config.yml          # Configuration
├── handlers/
│   ├── __init__.py
│   ├── query/          # Group query handlers by domain
│   │   ├── __init__.py
│   │   ├── chat.py
│   │   ├── rag.py
│   │   └── tools.py
│   ├── storage/        # Storage handlers
│   │   ├── __init__.py
│   │   └── documents.py
│   └── embed/          # Embedding handlers
│       ├── __init__.py
│       └── text.py
└── dependencies/       # Dependency initialization
    ├── __init__.py
    ├── llm.py
    └── vector_store.py
```

```python
# app.py
from whisk.kitchenai_sdk.kitchenai import KitchenAIApp
from handlers.query import chat, rag, tools
from handlers.storage import documents
from handlers.embed import text

# Initialize app
kitchen = KitchenAIApp(namespace="large-app")

# Register all handlers
chat.register_handlers(kitchen)
rag.register_handlers(kitchen)
tools.register_handlers(kitchen)
documents.register_handlers(kitchen)
text.register_handlers(kitchen)
```

```python
# handlers/query/chat.py
from whisk.kitchenai_sdk.schema import WhiskQuerySchema, WhiskQueryBaseResponseSchema, DependencyType

def register_handlers(kitchen):
    @kitchen.query.handler("chat")
    async def chat_handler(data: WhiskQuerySchema, llm=None) -> WhiskQueryBaseResponseSchema:
        """Basic chat handler"""
        ...

    @kitchen.query.handler("chat_stream")
    async def stream_handler(data: WhiskQuerySchema, llm=None) -> WhiskQueryBaseResponseSchema:
        """Streaming chat handler"""
        ...
```

### Pattern 2: Class-based Handlers

For more complex handlers that share state or utilities:

```python
# handlers/query/rag.py
from whisk.kitchenai_sdk.schema import WhiskQuerySchema, WhiskQueryBaseResponseSchema, DependencyType

class RAGHandlers:
    def __init__(self, kitchen):
        self.kitchen = kitchen
        self.register_handlers()
    
    def register_handlers(self):
        # Use instance method to share utilities
        self.kitchen.query.handler("rag")(self.rag_query)
        self.kitchen.query.handler("rag_stream")(self.rag_stream)
    
    async def rag_query(self, data: WhiskQuerySchema, llm=None, vector_store=None) -> WhiskQueryBaseResponseSchema:
        """RAG query handler"""
        docs = await self._get_relevant_docs(data.query, vector_store)
        return await self._generate_response(data.query, docs, llm)
    
    async def rag_stream(self, data: WhiskQuerySchema, llm=None, vector_store=None) -> WhiskQueryBaseResponseSchema:
        """Streaming RAG handler"""
        docs = await self._get_relevant_docs(data.query, vector_store)
        return await self._stream_response(data.query, docs, llm)
    
    async def _get_relevant_docs(self, query, vector_store):
        """Shared utility for document retrieval"""
        ...
    
    async def _generate_response(self, query, docs, llm):
        """Shared response generation logic"""
        ...

# app.py
from handlers.query.rag import RAGHandlers

rag_handlers = RAGHandlers(kitchen)
```

### Pattern 3: Router-based Organization

For grouping related handlers with shared dependencies:

```python
# handlers/query/tools.py
from typing import Protocol
from whisk.kitchenai_sdk.schema import WhiskQuerySchema, WhiskQueryBaseResponseSchema

class ToolRouter:
    def __init__(self, kitchen):
        self.kitchen = kitchen
    
    def register_handlers(self):
        # Register all tool handlers with shared prefix
        @self.kitchen.query.handler("tools/calculator")
        async def calculator(data: WhiskQuerySchema, llm=None):
            """Math calculation tool"""
            ...
        
        @self.kitchen.query.handler("tools/weather")
        async def weather(data: WhiskQuerySchema, llm=None):
            """Weather lookup tool"""
            ...
        
        @self.kitchen.query.handler("tools/search")
        async def search(data: WhiskQuerySchema, llm=None):
            """Web search tool"""
            ...

# app.py
from handlers.query.tools import ToolRouter

tool_router = ToolRouter(kitchen)
tool_router.register_handlers()
```

### Best Practices

1. **Handler Organization**:
   - Group related handlers in modules
   - Use clear naming conventions
   - Keep handler files focused and single-purpose

2. **Dependency Management**:
   - Initialize dependencies at app startup
   - Share dependencies across related handlers
   - Use dependency injection for testing

3. **Code Structure**:
   - Use classes for complex handlers with shared logic
   - Use routers for grouping related endpoints
   - Keep handler registration clear and explicit

4. **Testing**:
   - Test handlers in isolation
   - Use dependency injection for mocking
   - Group tests by handler module

5. **Documentation**:
   - Document handler purposes and requirements
   - Include example requests/responses
   - Document any special dependencies

This structure makes it easy to:
- Add new handlers without touching existing code
- Share utilities and dependencies between handlers
- Test handlers in isolation
- Maintain clear separation of concerns

## Sub-Apps and Modular Organization

Whisk supports a modular application structure through sub-apps, allowing you to organize handlers by domain and compose them together:

```python
from whisk.kitchenai_sdk.kitchenai import KitchenAIApp
from whisk.kitchenai_sdk.schema import (
    WhiskQuerySchema, 
    WhiskQueryBaseResponseSchema,
    DependencyType
)

# Create domain-specific sub-apps
chat_app = KitchenAIApp(namespace="chat")
rag_app = KitchenAIApp(namespace="rag")
tools_app = KitchenAIApp(namespace="tools")

# Define handlers in each sub-app
@chat_app.query.handler("basic")
async def basic_chat(data: WhiskQuerySchema, llm=None) -> WhiskQueryBaseResponseSchema:
    """Basic chat handler"""
    response = await llm.acomplete(data.query)
    return WhiskQueryBaseResponseSchema.from_llm_invoke(
        data.query,
        response.text
    )

@rag_app.query.handler("search")
async def rag_search(data: WhiskQuerySchema, llm=None, vector_store=None) -> WhiskQueryBaseResponseSchema:
    """RAG search handler"""
    docs = await vector_store.similarity_search(data.query)
    response = await llm.acomplete(data.query, context=docs)
    return WhiskQueryBaseResponseSchema.from_llm_invoke(
        data.query,
        response.text
    )

# Create main app and mount sub-apps
main_app = KitchenAIApp(namespace="main")
main_app.mount_app("chat", chat_app)    # Creates handler "chat.basic"
main_app.mount_app("rag", rag_app)      # Creates handler "rag.search"
main_app.mount_app("tools", tools_app)  # Creates handler "tools.calculator"
```

### Large Project Structure

For larger projects, organize sub-apps in separate modules:

```plaintext
my_project/
├── apps/
│   ├── __init__.py
│   ├── chat/
│   │   ├── __init__.py
│   │   ├── app.py          # chat_app definition
│   │   ├── handlers.py     # Chat handlers
│   │   └── utils.py        # Chat-specific utilities
│   ├── rag/
│   │   ├── __init__.py
│   │   ├── app.py          # rag_app definition
│   │   ├── handlers.py     # RAG handlers
│   │   └── retriever.py    # RAG-specific utilities
│   └── tools/
│       ├── __init__.py
│       ├── app.py          # tools_app definition
│       └── handlers.py     # Tool handlers
├── main.py                 # Main app composition
└── dependencies.py         # Shared dependencies
```

```python
# apps/chat/app.py
from whisk.kitchenai_sdk.kitchenai import KitchenAIApp
from .handlers import basic_chat, stream_chat

chat_app = KitchenAIApp(namespace="chat")
chat_app.query.handler("basic")(basic_chat)
chat_app.query.handler("stream")(stream_chat)
```

```python
# main.py
from whisk.kitchenai_sdk.kitchenai import KitchenAIApp
from apps.chat.app import chat_app
from apps.rag.app import rag_app
from apps.tools.app import tools_app
from dependencies import setup_dependencies

# Create main app
kitchen = KitchenAIApp(namespace="main")

# Setup shared dependencies
setup_dependencies(kitchen)

# Mount sub-apps
kitchen.mount_app("chat", chat_app)
kitchen.mount_app("rag", rag_app)
kitchen.mount_app("tools", tools_app)

# The resulting NATS subjects will be:
# - kitchenai.service.{client_id}.query.chat.basic
# - kitchenai.service.{client_id}.query.chat.stream
# - kitchenai.service.{client_id}.query.rag.search
# - kitchenai.service.{client_id}.query.tools.calculator
```

### Benefits of Sub-Apps

1. **Modularity**: Each sub-app can be developed and tested independently
2. **Organization**: Group related handlers and their dependencies
3. **Reusability**: Sub-apps can be reused across different projects
4. **Maintainability**: Easier to manage large codebases
5. **Isolation**: Each sub-app maintains its own namespace

### Dependency Management

Dependencies can be:
- Registered at the sub-app level for domain-specific dependencies
- Registered at the main app level for shared dependencies
- Automatically propagated to sub-apps when mounted

```python
# Register dependencies at sub-app level
chat_app.register_dependency(DependencyType.LLM, chat_llm)
rag_app.register_dependency(DependencyType.VECTOR_STORE, vector_store)

# Or register shared dependencies at main app level
main_app.register_dependency(DependencyType.LLM, shared_llm)
```

### Handler Labels

When mounting sub-apps, handler labels are automatically prefixed with the sub-app name:
- Original label: `"basic"` in chat_app
- Mounted label: `"chat.basic"` in main_app
- NATS subject: `kitchenai.service.{client_id}.query.chat.basic`

### Inter-Handler Dependencies

Handlers can depend on other handlers using the built-in NATS client for inter-handler communication:

```python
from whisk.client import WhiskClient
from whisk.kitchenai_sdk.schema import (
    WhiskQuerySchema, 
    WhiskStorageSchema,
    WhiskQueryBaseResponseSchema
)

# Create a RAG handler that depends on storage and embedding handlers
@rag_app.query.handler("answer")
async def rag_answer(
    data: WhiskQuerySchema, 
    llm=None, 
    client: WhiskClient=None  # Inject the NATS client
) -> WhiskQueryBaseResponseSchema:
    """RAG handler that uses other handlers for storage and embeddings"""
    
    # Use storage handler through NATS
    storage_response = await client.request(
        "storage.ingest",  # Will be prefixed with proper NATS subject
        WhiskStorageSchema(
            id="doc1",
            data=data.metadata.get("document"),
            metadata={"source": "rag_handler"}
        )
    )
    
    # Use embedding handler through NATS
    embed_response = await client.request(
        "embeddings.create",
        WhiskEmbedSchema(
            text=data.query,
            metadata={"type": "query"}
        )
    )
    
    # Use the results to generate final response
    response = await llm.acomplete(
        data.query,
        context=storage_response.data,
        embeddings=embed_response.embeddings
    )
    
    return WhiskQueryBaseResponseSchema.from_llm_invoke(
        data.query,
        response.text
    )

# The client is automatically injected by the WhiskClient when running the app
client = WhiskClient(
    nats_url="nats://localhost:4222",
    kitchen=kitchen
)
```

This pattern allows you to:
1. Compose complex handlers from simpler ones
2. Maintain loose coupling between handlers
3. Reuse functionality across different handlers
4. Scale handlers independently
5. Handle failures gracefully

### Best Practices for Inter-Handler Dependencies

1. **Error Handling**: Always handle potential failures from dependent handlers
2. **Timeouts**: Set appropriate timeouts for inter-handler requests
3. **Circuit Breaking**: Implement fallbacks for when dependent handlers fail
4. **Monitoring**: Track inter-handler dependencies for observability
5. **Documentation**: Document handler dependencies clearly

```python
# Example with better error handling and timeouts
@rag_app.query.handler("answer")
async def rag_answer(data: WhiskQuerySchema, llm=None, client: WhiskClient=None):
    try:
        # Set timeout for storage request
        storage_response = await client.request(
            "storage.ingest",
            WhiskStorageSchema(...),
            timeout=5.0  # 5 second timeout
        )
    except TimeoutError:
        # Fallback behavior
        logger.error("Storage handler timeout")
        storage_response = default_storage_response()
    except Exception as e:
        logger.error(f"Storage handler error: {e}")
        raise

    # Continue with embedding and response generation...