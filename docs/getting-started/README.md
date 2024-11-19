# Getting Started with KitchenAI 🚀

### 🌟 Motivation 

AI is revolutionizing software development, but integrating it into existing workflows can be challenging. KitchenAI eliminates the friction of building boilerplate code by providing:

- A **fully featured API server** with default routes.
- A **CLI** for quick setup.
- **Plugins** and other features to supercharge your workflow.

With KitchenAI, you can go from zero to API in **seconds**. Focus on the AI part, and let KitchenAI handle the rest.

---

### ⚡ Jumping In

KitchenAI's storage functions showcase how easy it is to get started.  

Built on top of **Django**, KitchenAI allows you to:

- Write **storage functions** with automatic file uploads.
- Seamlessly run tasks in **background workers**.
- Leverage Django's admin panel, ORM, and more without extra effort.

By focusing on the AI workflows, you can easily load files into a vector database.

---

### 🛠️ Example: Storage Function

Here’s an example of how KitchenAI simplifies integrating file uploads with vector storage and metadata:

```python
@kitchen.storage("file")
def chromadb_storage(dir: str, metadata: dict = {}, *args, **kwargs):
    """
    Store uploaded files into a vector store with metadata
    """
    parser = Parser(api_key=os.environ.get("LLAMA_CLOUD_API_KEY", None))

    response = parser.load(dir, metadata=metadata, **kwargs)

    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

    # Set up ChromaVectorStore and load in data
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
            
    # Create a quickstart index
    VectorStoreIndex.from_documents(
        response["documents"], 
        storage_context=storage_context, 
        show_progress=True,
        transformations=[
            TokenTextSplitter(), 
            TitleExtractor(), 
            QuestionsAnsweredExtractor()
        ]
    )
    
    return {"msg": "ok", "documents": len(response["documents"])}
```

---

### 🎉 What This Does

1. **File Uploads**: Automatically handles file uploads and processing.
2. **Vector Storage**: Stores data in a vector database with customizable metadata.
3. **Transformations**: Easily add NLP transformations like token splitting, title extraction, and more.

This simple storage function transforms into endpoints like the one shown below:

![File Endpoints](../../docs/_static/images/file-endpoints.png)

---

### 🌐 Ready to Dive In?

Let's get you started! The next step is to install KitchenAI and start building.
