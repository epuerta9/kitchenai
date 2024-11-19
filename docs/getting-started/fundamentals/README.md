# KitchenAI Fundamentals ⚡

## 🚀 Types of Functions

KitchenAI functions are the backbone of the framework. They form the building blocks of your AI-powered applications. Each function type comes with unique characteristics and serves specific use cases. Out of the box, you get support for the following:

- **📦 Storage Functions**  
- **🔍 Query Functions**  
- **🌐 Embed Functions**  

> 💡 *More function types are coming soon!*

These three types of functions provide the core functionality needed to build an AI application—**store**, **query**, and **embed** data seamlessly.

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
def query(request, data: QuerySchema):
    """Query the vector store for similar files"""
```

```python
@kitchen.query("simple-query-2")
def query_2(request, data: QuerySchema):
    """Query the vector store with a different technique"""
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

## 🌐 Embed Functions

**Embed functions** allow you to process non-file data, embedding it into a vector database for AI-driven use cases.

### 🔧 Function Signature

```python
@kitchen.embed("embed")
def embed(instance, metadata: dict = {}):
    """Embed the data"""
```

### 📂 Input Parameters

- **`instance`**: An `Embed Object` that contains the data to embed. 
```
    class EmbedObject(TimeStamped):
    """
    This is a model for any embed object that is created
    """
    class Status(models.TextChoices):
        PENDING = "pending"
        PROCESSING = "processing"
        COMPLETED = "completed"
        FAILED = "failed"

    text = models.CharField(max_length=255)
    ingest_label = models.CharField(max_length=255)
    status = models.CharField(max_length=255, default=Status.PENDING)
    metadata = models.JSONField(default=dict)

    def __str__(self):
        return self.text
```
- **`metadata`**: Metadata to associate with the embedding.  

### Example Usage

```python
@kitchen.embed("embed")
def embed_data(instance, metadata: dict = {}):
    """
    Embed non-file data into a vector database
    """
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    VectorStoreIndex.from_documents([instance], storage_context=storage_context)
    return "ok"
```

> 📘 More details about embed functions can be found [here](../../develop/ai-developer/README.md).

---


## The API

You can directly interact with the generated endpoints by going to `http://localhost:8000/api/docs`

## 🚀 Wrapping Up

With **Storage**, **Query**, and **Embed** functions, KitchenAI provides a powerful and flexible framework for building AI-powered applications. Get started today and let KitchenAI handle the heavy lifting, so you can focus on your AI workflows! 💡