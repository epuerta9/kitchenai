
---
<p align="center">
  <img src="docs/_static/images/logo.png" alt="KitchenAI" width="100" height="100">
</p>


# 🍽️ KitchenAI

[![Falco](https://img.shields.io/badge/built%20with-falco-success)](https://github.com/Tobi-De/falco)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Hatch Project](https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg)](https://github.com/pypa/hatch)

![](docs/_static/images/kitchenai-list.gif)

**Build AI Applications Faster!**

KitchenAI: Instantly turn your AI code into a production-ready API.

* For AI Developers: Focus solely on building your AI techniques like RAG—no need to worry about backend setup. Just write your functions, decorate them, and KitchenAI handles the rest with a scalable, production-ready API server.

* For App Developers: Integrate AI seamlessly with open-source APIs, leveraging KitchenAI’s robust foundations built on Django, background workers, and best-in-class frameworks.

> Compatible with ANY AI framework.

## Why?

Building AI applications is increasingly complex, with developers needing to master multiple frameworks like LangChain and LlamaIndex just to get solutions production-ready. This creates a barrier for app developers who want to integrate AI but lack the specialized expertise.

The common approach—using Jupyter Notebooks as "cookbooks"—is limited. Developers must manually extract, adapt, and rewrite code from these notebooks for their own use, which is time-consuming and inefficient.

KitchenAI simplifies this by letting AI developers write functions using familiar frameworks, decorated with KitchenAI syntax. It then automatically generates a production-ready API, using proven technologies to handle the backend. This removes the need for developers to understand the complexities of HTTP or build their own servers, allowing seamless AI integration with minimal effort.



> _For those that do want more control, you have complete access to request objects, django ninja routers, and other django internals if your use case needs it._

## Project Status

We are still in alpha and welcome contributions, thoughts, suggestions. Check out our shortlist for project roadmap [Roadmap](#roadmap)

## ⚡ Quickstart

### Step 1: Export Variables

#### Your OpenAI API Key

KitchenAI’s demo uses OpenAI as the LLM provider. Set your OpenAI key in your environment:

```bash
export OPENAI_API_KEY=<your key>
```

> _Feel free to customize this with other LLM providers as needed!_

#### KitchenAI DEBUG

Set the KitchenAI DEBUG environment variable to `true` to enable debug logging:

```bash
export KITCHENAI_DEBUG=True
```

### Step 2: Install KitchenAI


```bash
python -m venv venv && source venv/bin/activate && pip install kitchenai
```

### Step 3: Browse Available Projects

```bash
kitchenai cook list && kitchenai cook select llama-index-chat
```
![](docs/_static/images/kitchenai-list.gif)


### Step 4: Init Environment

```bash
kitchenai init && kitchenai dev --module app:kitchen
```
![](docs/_static/images/kitchenai-dev.gif)

An entire API server is spun up in seconds.

![](docs/_static/images/openapi.png)

### Step 5: Build A Docker Container

```bash
kitchenai build . app:kitchenai
```

![](docs/_static/images/kitchenai-build.gif)

the container will be named kitchenai-app


## 🚀 Features
- **Quick Cookbook Creation**: Spin up new cookbooks with one command.
- **Production-Ready AI**: Turn your ideas into robust, AI-driven endpoints.
- **Extensible Framework**: Easily add your custom recipes and integrate them into your apps.
- **Containerized Deployment**: Build Docker containers and share your cookbooks effortlessly.


## 🚀 Under the Hood Magic

KitchenAI is built with a powerful stack of technologies that provide flexibility, performance, and ease of deployment—all optimized for a modern AI development workflow:

- **⚡ Async Django (v5.0+)**: Leveraging the battle-tested Django framework for unparalleled reliability and flexibility. Built for async operations, allowing you to scale and extend your application effortlessly.

- **🌀 Django Ninja**: Streamlined, async-first API framework. With Django Ninja, async functions come as the default, enabling you to build high-performance APIs without the hassle.

- **⚙️ Django Q2**: A robust task broker that lets you offload long-running processes and background tasks with ease, ensuring your application remains fast and responsive.

- **🔧 S6 Overlay**: The ultimate Docker process supervisor. S6 Overlay bundles KitchenAI into a compact and efficient container, managing processes gracefully to ensure everything runs smoothly, even under heavy loads.


## Developer Experience

![Developer Flow](docs/_static/images/developer-flow.png)

---


## 🍳 KitchenAI Types

KitchenAI provides a standard interface between developers and AI functions through API endpoints. With these powerful types, you can easily decorate your functions and turn them into production-ready APIs. The available KitchenAI types include:

1. **Storage**: Store and manage data easily.
2. **Embedding**: Generate and work with vector embeddings.
3. **Agent**: Build and manage autonomous agents.
4. **Query**: Execute AI-powered queries and retrieve responses.

---

## 🗂️ Storage Type


### Example Usage

```python
from ninja import Router, Schema, File
from kitchenai.contrib.kitchenai_sdk.kitchenai import KitchenAIApp
from ninja.files import UploadedFile

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext
from llama_index.vector_stores.chroma import ChromaVectorStore

from llama_index.llms.openai import OpenAI
import os
import tempfile
import chromadb

# Set up ChromaDB client and a new collection
chroma_client = chromadb.EphemeralClient()
chroma_collection = chroma_client.create_collection("quickstart")
llm = OpenAI(model="gpt-4")

# Use Django Ninja Schemas to define the Request Body
class Query(Schema):
    query: str

kitchen = KitchenAIApp()

# This decorator uniquely identifies your function as an API route.
@kitchen.storage("storage")
def chromadb_storage(request, file: UploadedFile = File(...)):
    """
    Store uploaded files into a vector store
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_file_path = os.path.join(temp_dir, file.name)

        with open(temp_file_path, "wb") as temp_file:
            for chunk in file.chunks():
                temp_file.write(chunk)

        documents = SimpleDirectoryReader(input_dir=temp_dir).load_data()

    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    VectorStoreIndex.from_documents(documents, storage_context=storage_context)

    return {"msg": "ok"}
```

This code creates a storage endpoint where uploaded files are stored as vector embeddings in a Chroma vector store. KitchenAI manages everything, making your AI functions accessible via API.

---

## 💬 Chat Type


```python
# Async Function
@kitchen.query("query")
async def query(request, query: Query):
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

    index = VectorStoreIndex.from_vector_store(vector_store)

    chat_engine = index.as_chat_engine(chat_mode="best", llm=llm, verbose=True)
    response = await chat_engine.achat(query.query)

    return {"msg": response.response}
```

This code snippet turns your function into an API that processes chat queries using a vector store, returning responses dynamically.

---

## 📝 API Documentation

The above functions translate to the following OpenAPI Spec

### OpenAPI Specification (Click to Expand)


```json
{
  "openapi": "3.1.0",
  "info": {
    "title": "KitchenAI API",
    "version": "1.0.0",
    "description": "A powerful API for building and managing AI cookbooks"
  },
  "paths": {
    "/api/health": {
      "get": {
        "operationId": "kitchenai_api_default",
        "summary": "Default",
        "responses": {
          "200": {
            "description": "OK"
          }
        }
      }
    },
    "/api/custom/default/storage/storage": {
      "post": {
        "operationId": "kitchenai_chromadb_storage",
        "summary": "ChromaDB Storage",
        "description": "Store uploaded files into a vector store",
        "requestBody": {
          "content": {
            "multipart/form-data": {
              "schema": {
                "properties": {
                  "file": {
                    "format": "binary",
                    "title": "File",
                    "type": "string"
                  }
                },
                "required": ["file"],
                "title": "FileParams",
                "type": "object"
              }
            }
          },
          "required": true
        },
        "responses": {
          "200": {
            "description": "OK"
          }
        }
      }
    },
    "/api/custom/default/query/query": {
      "post": {
        "operationId": "kitchenai_query",
        "summary": "Query",
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/Query"
              }
            }
          },
          "required": true
        },
        "responses": {
          "200": {
            "description": "OK"
          }
        }
      }
    }
  },
  "components": {
    "schemas": {
      "Query": {
        "properties": {
          "query": {
            "title": "Query",
            "type": "string"
          }
        },
        "required": ["query"],
        "title": "Query",
        "type": "object"
      }
    }
  },
  "servers": []
}
```





---

### 💡 Tip:
Add any necessary dependency containers to fit your specific use case and requirements!



### Deployments

Since this project is still in alpha, it is recommended at this time to deploy as a sidecar with minimal external access.


# Roadmap

The following is our roadmap list of features.

* Client SDK
* Django Q2 worker integration
* Signals framework for kitchenai functions
* Custom App plugins - Testing, other native integrations

---

## 🧑‍🍳 Contribution Project Setup


## Pre-reqs

* Just
* hatch
* Python 3.11+

Make sure the Python version in your `.pre-commit-config.yaml` file matches the version in your virtual environment. If you need to manage Python installations, Hatch has you covered: [Managing Python with Hatch](https://hatch.pypa.io/latest/tutorials/python/manage/).

To set up your project:

```bash
just bootstrap && just setup
```

This command sets up your virtual environment, installs dependencies, runs migrations, and creates a superuser (`admin@localhost` with password `admin`).


---

## 🙏 Acknowledgements

This project draws inspiration from the [Falco Project](https://github.com/Tobi-De/falco), and incorporates best practices and tools from across the Python ecosystem.

> 💡 **Pro Tip**: Run `just` to see all available commands and streamline your development workflow!
