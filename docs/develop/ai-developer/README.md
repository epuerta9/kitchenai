# KitchenAI: Framework-Agnostic AI Development 🚀

KitchenAI is designed to be **framework-agnostic**, providing a straightforward, standard interface that bridges the gap between **AI developers** and **application developers**. Its mission is to enable seamless collaboration through a **common, production-ready backend** for AI workflows.

---

## ⚙️ **KitchenAI Core**

The **KitchenAI Core** is the backbone of the framework. It’s built as a Django app and powers key functionalities, such as:
- Emitting **signals** for event-driven workflows.
- Importing **cookbooks**.
- Handling the backend logic seamlessly.

🔧 **Coming Soon**: A guide to using KitchenAI Core signals for building **event-driven architectures** and scalable applications.

---

## 📂 **Storage: Smarter Background Workers**

Storage functions in KitchenAI run as **background tasks**, ensuring smooth, non-blocking operations. But KitchenAI takes it further by enabling you to define **hooks** for post-task business logic.

### Example: Storage Functions with Hooks

1️⃣ Define a **storage function**:
```python
@kitchen.storage("file")
def chromadb_storage(dir: str, metadata: dict = {}, *args, **kwargs):
    """
    Store uploaded files into a vector store with metadata
    """
```

2️⃣ Add a **storage hook** with the same label to handle the results:
```python
@kitchen.storage_hook("file")
def chromadb_hook(task):
    """
    Add the result to a vector store
    """
```

💡 **How It Works**:
- Hooks leverage **Django Q tasks and hooks**, offering powerful post-task processing.
- Easily extend workflows by adding business logic to storage outcomes.

📘 [Dive deeper into Django Q hooks.](https://django-q.readthedocs.io/en/latest/)

---

## 🌱 **What’s Next?**

KitchenAI is continually evolving to provide more tools for developers. Here’s what’s on the horizon:

- **Agents**: Build task-driven AI workflows.
- **Techniques**: Support for more advanced AI patterns.
  - Query techniques
  - Embedding techniques

---

KitchenAI is your partner in simplifying AI development, letting you focus on creating amazing features while the framework handles the heavy lifting. 💼

