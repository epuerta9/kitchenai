
---
# 🍽️ KitchenAI

[![Falco](https://img.shields.io/badge/built%20with-falco-success)](https://github.com/Tobi-De/falco)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Hatch Project](https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg)](https://github.com/pypa/hatch)

**Your AI Kitchen for Production-Ready Cookbooks!**

KitchenAI is designed to make building, sharing, and consuming AI-powered cookbooks easy, efficient, and scalable. Whether you want to quickly prototype AI solutions or deploy robust applications, KitchenAI provides a hardened application runtime so you only focus on authoring AI code in simple functions that are completely AI framework agnostic.


## Why? 

The complexity of building AI applications has significantly increased in recent years due to the growing number of frameworks, techniques, and tools required to make solutions production-ready. While these frameworks, such as LangChain and LlamaIndex, are essential for delivering high-quality AI applications, they often demand specialized knowledge. This creates a substantial burden for application developers who aim to integrate AI into their products but may lack the specific expertise needed.

The current common approach is to provide a collection of AI "cookbooks" in Jupyter Notebook format. While these resources are helpful for learning, they are not readily usable in production by other developers. To integrate such code, developers must read through the notebooks, extract relevant sections, and adapt the code to fit their own applications—assuming they are working in the same programming language. This process is time-consuming, inefficient, and often frustrating.

A more efficient solution is to allow AI developers to write kitchenai-decorated functions within their preferred frameworks, automatically generating a production-ready API. This approach uses proven technologies in a structured, opinionated manner to create an API server that abstracts away the complexities of HTTP semantics. The result is a streamlined development process, enabling seamless integration of AI capabilities into applications without the need for extensive, specialized knowledge.

> _For those that do want more control, you have complete access to request objects, django ninja routers, and other django internals if your use case needs it._

## Project Status

We are still in alpha and welcome contributions, thoughts, suggestions. Check out our shortlist for project roadmap [Roadmap](#roadmap)

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

![Developer Flow](./docs/images/developer-flow.png)

---

## 📋 Prerequisites

Before you start, make sure you have the following:

- Python `3.11+`
- [Hatch 1.9.1+](https://hatch.pypa.io/latest/)
- [Just](https://github.com/casey/just) task runner



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

<details>
  <summary>View OpenAPI Spec</summary>

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

</details>


## ⚡ Quickstart

### Step 1: Export Your OpenAI API Key

KitchenAI’s demo uses OpenAI as the LLM provider. Set your OpenAI key in your environment:

```bash
export OPENAI_API_KEY=<your key>
```

> _Feel free to customize this with other LLM providers as needed!_

### Step 2: Install KitchenAI

Install the application globally using `pipx`:

```bash
pipx install kitchenai
```

### Step 3: Create a New Cookbook

```bash
kitchenai new
```

Cookbooks are prefixed with `kitchenai_<project_name>` for easy identification and organization.

### Step 4: Bootstrap Your Development Environment

```bash
just bootstrap
```

This sets up Python environments using Hatch:
- `default` environment
- `dev` environment for active development

### Step 5: Enter Your Development Environment

```bash
hatch shell dev
```

This is equivalent to activating a virtual environment (`source venv/bin/activate`)—but better!

### Step 6: Initialize Your Cookbook

```bash
kitchenai init
```

KitchenAI reads your `kitchenai.yml` file and stores the metadata locally in an SQLite database, readying your project for execution.

### Step 7: Run Your Cookbook

```bash
kitchenai dev
```

This command imports your cookbook module and transforms your functions into production-ready endpoints, adhering to best practices.

---

## 🛠️ Building and Sharing

Ready to share your AI magic with the world? KitchenAI makes it simple to package and deploy your cookbooks!

### Step 1: Build a Python Wheel

```bash
hatch build
```

This creates a distributable `.whl` package, ready for publishing to PyPI.

### Step 2: Build a Docker Container

```bash
hatch run docker-build
```

With these two commands, you can quickly prepare your AI solutions for deployment and distribution!

---

## 🐳 Running Docker Compose

Once your image is built, you can run it with Docker Compose. Add any dependencies your cookbook requires, and spin up your environment:

```bash
docker compose up -d
```

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

## 🧑‍🍳 Project Setup

Make sure the Python version in your `.pre-commit-config.yaml` file matches the version in your virtual environment. If you need to manage Python installations, Hatch has you covered: [Managing Python with Hatch](https://hatch.pypa.io/latest/tutorials/python/manage/).

To set up your project:

```bash
just setup
```

This command sets up your virtual environment, installs dependencies, runs migrations, and creates a superuser (`admin@localhost` with password `admin`).

### Running the Django Development Server

```bash
just server
```

This launches the Django development server, making it easy to test your application locally.

---

## 🙏 Acknowledgements

This project draws inspiration from the [Falco Project](https://github.com/Tobi-De/falco), and incorporates best practices and tools from across the Python ecosystem.

> 💡 **Pro Tip**: Run `just` to see all available commands and streamline your development workflow!

