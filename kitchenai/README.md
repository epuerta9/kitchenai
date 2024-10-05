# KitchenAI Client SDK

KitchenAI Client SDK is a Python library that allows you to easily interact with KitchenAI cookbooks. It provides a simple interface for querying, storing, embedding, and running AI models defined in KitchenAI cookbooks.

## Installation

Install the KitchenAI Client SDK using pip:

```bash
pip install kitchenai
```

## Quick Start

Here's a simple example to get you started with the KitchenAI Client SDK:

```python
from kitchenai import KitchenClient

# Initialize the client
with KitchenClient(app_id="myapp", namespace="default") as client:
    # Perform a query
    response = client.query("What's the weather like today?", "weather-query")
    print(response)

    # Upload a file
    file_response = client.upload_file("/path/to/document.pdf", "document-upload")
    print(file_response)
```

## Features

- Query AI models
- Store and retrieve data
- Generate embeddings
- Run custom AI workflows
- Upload and process files

## Detailed Usage

### Initialization

```python
from kitchenai import KitchenClient

client = KitchenClient(app_id="myapp", namespace="default")
```

### Querying

```python
response = client.query("Translate 'Hello' to French", "translation-query")
print(response)
```

### Storage Operations

```python
data = {"key": "value"}
response = client.storage("store-data", **data)
print(response)
```

### Embedding Generation

```python
text = "This is a sample text for embedding"
response = client.embedding("generate-embedding", text=text)
print(response)
```

### Running Custom Workflows

```python
params = {"param1": "value1", "param2": "value2"}
response = client.runnable("custom-workflow", **params)
print(response)
```

### File Upload

```python
response = client.upload_file("/path/to/image.jpg", "image-analysis")
print(response)
```

## Configuration

You can configure the KitchenClient with custom settings:

```python
config = {
    "timeout": 30,
    "retry_attempts": 5
}
client = KitchenClient(config=config, app_id="myapp", namespace="production")
```

## Error Handling

The SDK uses a retry mechanism for network-related errors. You can catch exceptions for more specific error handling:

```python
try:
    response = client.query("Some query", "some-label")
except Exception as e:
    print(f"An error occurred: {e}")
```

## Best Practices

1. Use the context manager (`with` statement) to ensure proper initialization and cleanup.
2. Set appropriate timeouts for your use case.
3. Handle exceptions in your application code.
4. Use descriptive labels for your operations to easily identify them in logs and debugging.

## Contributing

We welcome contributions to the KitchenAI Client SDK! Please see our [Contributing Guidelines](CONTRIBUTING.md) for more details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support, please open an issue on our [GitHub repository](https://github.com/kitchenai/client-sdk) or contact our support team at support@kitchenai.com.

---

Happy cooking with KitchenAI! 🍳🤖