# KitchenAI SDK

KitchenAI SDK is a powerful tool for authoring and defining AI cookbooks in well-defined stages. It allows you to easily create portable AI frameworks that can run alongside your code as a sidecar.

## Features

- Wrap FastAPI applications with KitchenAI functionality
- Define query, storage, embedding, and runnable endpoints
- Automatic Pydantic model integration for request body parsing
- Metadata management for easy discovery of endpoints
- Support for both synchronous and asynchronous handlers

## Installation

Install the KitchenAI SDK using pip:

```bash
pip install kitchenai-sdk
```

## Quick Start

Here's a simple example to get you started with the KitchenAI SDK:

```python
from fastapi import FastAPI, Request
from kitchenai_sdk import KitchenAIApp
from pydantic import BaseModel

app = FastAPI()
kitchen = KitchenAIApp(app_instance=app)

class QueryRequest(BaseModel):
    query: str

@kitchen.query("simple-query")
def simple_query(request: Request, body: QueryRequest):
    return {"result": f"Processed query: {body.query}"}

# Run with: uvicorn main:app
```

## Detailed Usage

### Initialization

```python
from fastapi import FastAPI
from kitchenai_sdk import KitchenAIApp

app = FastAPI()
kitchen = KitchenAIApp(app_instance=app, namespace="my-cookbook")
```

### Defining Endpoints

KitchenAI SDK provides decorators for different types of endpoints:

#### Query Endpoint

```python
@kitchen.query("my-query")
async def my_query(request: Request, body: QueryRequest):
    # Your query logic here
    return {"result": "Query processed"}
```

#### Storage Endpoint

```python
@kitchen.storage("store-data")
async def store_data(request: Request):
    # Your storage logic here
    return {"status": "Data stored"}
```

#### Embedding Endpoint

```python
@kitchen.embedding("generate-embedding")
def generate_embedding(request: Request):
    # Your embedding logic here
    return {"embedding": [0.1, 0.2, 0.3]}
```

#### Runnable Endpoint

```python
@kitchen.runnable("custom-workflow")
async def custom_workflow(request: Request):
    # Your custom workflow logic here
    return {"status": "Workflow completed"}
```

### Using Pydantic Models

KitchenAI SDK automatically detects Pydantic models in your function signatures:

```python
class MyModel(BaseModel):
    field1: str
    field2: int

@kitchen.query("pydantic-example")
def pydantic_example(request: Request, body: MyModel):
    return {"received": body.dict()}
```

### Streaming Responses

You can use StreamingResponse for long-running or real-time operations:

```python
from fastapi.responses import StreamingResponse

@kitchen.query("streaming-query")
def streaming_query(request: Request, body: QueryRequest):
    def generate():
        for i in range(10):
            yield f"Data chunk {i}\n"
    
    return StreamingResponse(generate(), media_type="text/plain")
```

## Best Practices

1. Use descriptive labels for your endpoints to make them easily discoverable.
2. Leverage Pydantic models for request validation and documentation.
3. Implement proper error handling in your endpoint functions.
4. Use asynchronous functions for I/O-bound operations to improve performance.
5. Organize your cookbook into logical sections using the different endpoint types.

## Running Your Cookbook

To run your KitchenAI cookbook:

1. Create your FastAPI app and KitchenAI wrapper as shown in the examples.
2. Run your app using an ASGI server like Uvicorn:

```bash
uvicorn main:app --reload
```

3. Your KitchenAI endpoints will be available under the specified namespace, e.g., `/default/query/my-query`.

## Contributing

We welcome contributions to the KitchenAI SDK! Please see our [Contributing Guidelines](CONTRIBUTING.md) for more details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support, please open an issue on our [GitHub repository](https://github.com/kitchenai/sdk) or contact our support team at support@kitchenai.com.

---

Happy cooking with KitchenAI! 🍳🤖