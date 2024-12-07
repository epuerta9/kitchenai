# KitchenAI Fundamentals ⚡

## Jupyter Notebook Magic Commands for KitchenAI

The following documentation provides a comprehensive guide to the custom Jupyter Notebook magic commands available for quickly iterating and creating **KitchenAI modules**. These commands streamline the development process by integrating with Django models and utilizing AI-powered tools to generate modular, production-ready code.

---

> 💡 *Note: These commands are only available in Jupyter notebooks.*

## Getting Started

To help you get started quickly, we provide example notebooks in our community repository. Check out our [LlamaIndex starter notebook](https://github.com/epuerta9/kitchenai-community/blob/main/src/kitchenai_community/llama_index_starter/notebook.ipynb) for a complete example of using KitchenAI with LlamaIndex.

This example demonstrates:
- Setting up a project
- Registering functions with different types and labels
- Importing required libraries
- Configuring the environment
- Generating a complete module

### **Setup and Environment**
    - load the extension `%load_ext kitchenai.contrib.cook`
    - set the project `%kitchenai_set_project MyProject`

---

### **Available Commands**

#### **1. Line Magic Commands**
These commands are executed with a single `%` prefix.

##### **`%kitchenai_set_project <project_name>`**
Sets the active project for registering and generating KitchenAI modules.

- **Usage:**
  ```python
  %kitchenai_set_project MyProject
  ```
- **Output:**  
  - Creates a new project (if it doesn't exist).
  - Sets the current project context.

---

##### **`%kitchenai_get_project`**
Retrieves details about the currently set project.

- **Usage:**
  ```python
  %kitchenai_get_project
  ```
- **Output:**  
  - Returns the project's metadata or an error if the project does not exist.

---

##### **`%kitchenai_llm_model <provider> <model>`** 
Optional: Sets the LLM provider and model used for generating modules. 
Sets the LLM provider and model used for generating modules. 

To use ollama, you need to have ollama installed and running. You can install the client library with with `pip install llama-index-llms-ollama`.

> 💡 *Note: The default provider is `openai` and the default model is `gpt-4`. Leave this blank to use the default.*

> 💡 *Note: The `provider` can be either `openai` or `ollama`.*

- **Usage:**
  ```python
  %kitchenai_llm_model openai gpt-3.5-turbo
  ```
  or 
  ```python
  %kitchenai_llm_model ollama llama3
  ```
- **Output:**  
  Updates the LLM configuration for subsequent commands.

---

##### **`%kitchenai_create_module [verbose]`**
Generates a `app.py` module using registered functions, imports, and setups in the current project.

> 💡 *Note: The `verbose` flag is optional. If not provided, the output will be more concise.*

> 💡 *Note: This should be the last command in your notebook.*

- **Usage:**
  ```python
  %kitchenai_create_module verbose
  ```
- **Output:**  
  - Creates an `app.py` file using templates and AI-generated code.  
  - Prints the prompt and AI-generated response if `verbose` is specified.

---

#### **2. Cell Magic Commands**
These commands are executed with a `%%` prefix and apply to the content in the cell.

##### **`%%kitchenai_register <type> <label>`**
Registers a function under a specific type (e.g., `storage`, `query`) and label for the current project.

- **Usage:**
  ```python
  %%kitchenai_register query my-function
  def my_function(data):
      return data * 2
  ```
- **Output:**  
  - Saves the function code and metadata to the database.
  - Updates existing entries if the function code changes.


Available types: `storage`, `query`, `embedding`, and `agent`.
---

##### **`%%kitchenai_import <label>`**
Registers an import block for the current project.

- **Usage:**
  ```python
  %%kitchenai_import utilities
  import numpy as np
  import pandas as pd
  ```
  or
  ```python
  %%kitchenai_import utilities
    from llama_index.core import VectorStoreIndex, StorageContext
    from llama_index.vector_stores.chroma import ChromaVectorStore
    from llama_index.llms.openai import OpenAI
    import os 
    import chromadb
    from llama_index.llms.openai import OpenAI
    from llama_index.core.node_parser import TokenTextSplitter
    from llama_index.core.extractors import (
        TitleExtractor,
        QuestionsAnsweredExtractor)

    from llama_index.core import Document
    from kitchenai.contrib.kitchenai_sdk.storage.llama_parser import Parser 
    ```
- **Output:**  
  - Saves the import block with the specified label.
  - Updates existing entries if the code changes.

---

##### **`%%kitchenai_setup <label>`**
Registers a setup block (e.g., initialization or configuration code) for the current project.

- **Usage:**
  ```python
  %%kitchenai_setup vector_db
    chroma_client = chromadb.PersistentClient(path="chroma_db")
    chroma_collection = chroma_client.get_or_create_collection("quickstart")



    llm = OpenAI(model="gpt-4")
  ```
- **Output:**  
  - Saves the setup code with the specified label.
  - Updates existing entries if the code changes.

---

### **Behind the Scenes**

#### **Magic Commands Workflow**

1. **Project Management:**  
   Use `%kitchenai_set_project` to set the project context. All subsequent commands will operate within this context.

2. **Code Registration:**  
   Use cell magic commands (`%%kitchenai_register`, `%%kitchenai_import`, `%%kitchenai_setup`) to register functions, imports, and setups to the current project. These commands check for changes using a SHA-256 hash.

3. **Module Generation:**  
   Use `%kitchenai_create_module` to compile all registered code into a `app.py` file. This leverages predefined templates and an LLM for code generation. Making it easy to generate a production-ready module.

---


This powerful set of commands allows for rapid prototyping, testing, and deployment of KitchenAI modules directly within Jupyter notebooks!

## 🚀 Types of Functions

KitchenAI functions are the backbone of the framework. They form the building blocks of your AI-powered applications. Each function type comes with unique characteristics and serves specific use cases. Out of the box, you get support for the following:

- **📦 Storage Functions**  
- **🔍 Query Functions**  
- **🌐 Embed Functions**  
- **🤖 Agent Functions**  


These four types of functions provide the core functionality needed to build an AI application—**store**, **query**, **embedding**, and **agent** data seamlessly.

---

## 🏷️ Function Labels: The Secret Sauce

Every function in KitchenAI is **labeled** with a unique string, making it easy to identify in your API or code. Labels allow for **flexibility and customization**, letting you expose similar logic through different endpoints.

For example:
- You can store data in **two different databases** using functions with the same logic but different labels.  
- You can use **different query techniques** on the same underlying data.

### Example: Storage Functions with Different Labels

```python
@kitchen.storage("chroma-db")
def chroma_storage(dir: str, metadata: dict = {}, *args, **kwargs):
    """Store files in a vector database"""
```

```python
@kitchen.storage("chroma-db-2")
def chroma_storage_2(dir: str, metadata: dict = {}, *args, **kwargs):
    """Store files in a second vector database"""
```

### Example: Query Functions with Different Labels

```python
@kitchen.query("simple-query")
def query(data: QuerySchema):
    """Query the vector store for similar files"""
```

```python
@kitchen.query("simple-query-2")
def query_2(data: QuerySchema):
    """Query the vector store with a different technique"""
```

### Example: Embed Functions with Different Labels

```python
@kitchen.embed("simple-embed")
def simple_embed(instance: EmbedSchema, metadata: dict = {}, **kwargs):
    return {"ok": instance.text}
```

Labels make it easy to manage and organize multiple endpoints tailored to your needs.

---

## 📦 Storage Functions

**Storage functions** handle file uploads and data storage. They let you store files in a database, file system, or any other storage system—with minimal effort.

By default, storage functions:
- Run in **background workers**.  
- Are **non-blocking**, so your API remains fast.  
- Automatically handle **file uploads**.

### 🔧 Function Signature

```python
@kitchen.storage("file")
def chromadb_storage(dir: str, metadata: dict = {}, *args, **kwargs):
    """
    Store uploaded files into a vector store with metadata
    """
```

### 📂 Input Parameters

- **`dir`**: Directory containing the files to be stored.  
- **`metadata`**: Metadata to associate with the stored files.  

### Example Usage

```python
@kitchen.storage("file")
def store_files(dir: str, metadata: dict = {}, *args, **kwargs):
    parser = Parser(api_key=os.environ.get("LLAMA_CLOUD_API_KEY", None))
    response = parser.load(dir, metadata=metadata, **kwargs)

    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    VectorStoreIndex.from_documents(
        response["documents"],
        storage_context=storage_context,
        show_progress=True
    )

    return {"msg": "ok", "documents": len(response["documents"])}
```

> 📘 More details about storage functions can be found [here](../../develop/ai-developer/README.md).

---

## 🔍 Query Functions

**Query functions** are used to fetch data from your storage systems. They are the interface for your AI application's search or Q&A functionalities.

### 🔧 Function Signature

```python
@kitchen.query("simple-query")
async def query(request, data: QuerySchema):
    """Query the vector store for similar files"""
```

### 🛠️ Synchronous or Asynchronous? Your Choice!  

KitchenAI supports both sync and async query functions:

- **Async Example**:  
  ```python
  @kitchen.query("simple-query")
  async def query(request, data: QuerySchema):
      """Query the vector store"""
  ```

- **Sync Example**:  
  ```python
  @kitchen.query("simple-query")
  def query(request, data: QuerySchema):
      """Query the vector store"""
  ```

### 📂 Input Parameters

- **`request`**: The Django `request` object.  
- **`data`**: A schema defining the query (e.g., `QuerySchema`).  

### Example Usage

```python
@kitchen.query("simple-query")
def query_files(request, data: QuerySchema):
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    index = VectorStoreIndex.from_vector_store(vector_store)

    return index.query(data.query)
```

> 📘 More details about query functions can be found [here](../../develop/ai-developer/README.md).

---

## 🤖 Agent Functions

**Agent functions** allow you to create custom agents to handle complex workflows.
They have the same signature as query functions, but they are designed to handle more complex workflows.


### 🔧 Function Signature

```python
@kitchen.agent("simple-agent")
def simple_agent(data: QuerySchema):
    """Run a simple agent"""
```

---

## 🌐 Embedding Functions

**Embed functions** allow you to process non-file data, embedding it into a vector database for AI-driven use cases.

### 🔧 Function Signature

```python
@kitchen.embed("simple-embed")
def simple_embed(instance: EmbedSchema, metadata: dict = {}, **kwargs):
    return {"ok": instance.text}
```

### 📂 Input Parameters

- **`instance`**: An `Embed Schema` that contains the data to embed. 
```
    class EmbedSchema(Schema):
        text: str
        metadata: dict[str, str] | None = None

```
- **`metadata`**: Metadata to associate with the embedding.  

### Example Usage

```python
@kitchen.embed("embed")
def embed_data(instance: EmbedSchema, metadata: dict = {}):
    """
    Embed non-file data into a vector database
    """
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    documents = [Document(text=instance.text, metadata=instance.metadata)]
    VectorStoreIndex.from_documents(documents, storage_context=storage_context)
    return "ok"
```

> 📘 More details about embed functions can be found [here](../../develop/ai-developer/README.md).

---


## The API

You can directly interact with the generated endpoints by going to `http://localhost:8001/api/docs`

## 🚀 Wrapping Up

With **Storage**, **Query**, **Agent**, and **Embedding** functions, KitchenAI provides a powerful and flexible framework for building AI-powered applications. Get started today and let KitchenAI handle the heavy lifting, so you can focus on your AI workflows! 💡
