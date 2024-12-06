# 🌟 Customizing KitchenAI

KitchenAI provides extensive customization options to make it fit your application's specific needs. Here's a concise guide to its key features and how to make the most of them! 🚀

---

## 🔧 **KitchenAI `app.py`: The Heart of Customization**

The `app.py` file is the main entry point for your KitchenAI application. It's where you configure and customize the framework.

```python
from kitchenai.contrib.kitchenai_sdk.kitchenai import KitchenAIApp

app = KitchenAIApp()
```

---

## 🔄 **BYOR: Bring Your Own Routes (COMING SOON)**

KitchenAI uses **Django Ninja** for its API framework, allowing you to seamlessly integrate your own custom endpoints. We are working on a guide to add additonal hooks to the router.

### ✨ Example: Adding a Custom Route
```python
from ninja import Router

router = Router()

@router.get("/hello")
def hello(request):
    return {"message": "Hello, World!"}

app = KitchenAIApp(router=router)
```

✅ **Benefits:**
- Full flexibility to build your own API.
- Integrates with Django’s routing and middleware system.

🔮 **COMING SOON: Enhanced Route Customization**
- Support for route versioning
- Middleware hooks
- Custom error handling
- Rate limiting and throttling

---

## 🛠️ **Django Admin: Manage Your Data Easily**

The **Django Admin Interface** comes pre-configured for core KitchenAI objects and plugins.

### 🔑 Steps to Access:
1. Navigate to: `http://localhost:8001/kitchenai-admin`

### ✨ Create a Superuser the same way you would for Django:
```bash
kitchenai manage createsuperuser
```

The default admin for local development can be created by running  
```bash
kitchenai setup
```

This will create a superuser with the username `admin@localhost` and the password `admin`.

---

## 📡 Signals

KitchenAI uses Django Signals to hook into certain actions making it easy to build applications that react to changes. 

### Query Signals

Query endpoints trigger two signals:
- `query_input_signal`
- `query_output_signal`

They can be listened to with the following decorators:

```python
@receiver(query_input_signal)
def my_signal_handler(sender, **kwargs):
    print(f"Signal received from {sender}. Additional data: {kwargs}")
```

```python
@receiver(query_output_signal)
def my_signal_handler(sender, **kwargs):
    print(f"Signal received from {sender}. Additional data: {kwargs}")
```

---

## 🖥️ **KitchenAI Management Commands**

KitchenAI CLI is packed with powerful management commands. To explore:
```bash
kitchenai manage
```

✅ **Features**:
- Manage migrations
- Run the development server
- Work with Django Q clusters for background tasks.

---

## 🧩 **Plugins: Extend with Ease**

KitchenAI supports **Django DJP plugins** [](https://djp.readthedocs.io/en/latest/) to extend its functionality.

### ✨ How to Add a DJP enabled Plugin
1. Install your plugin:
   ```bash
   pip install <your_plugin>
   ```
2. The plugin automatically integrates with KitchenAI.

### 🔮 **Roadmap for Plugins**:
- Third-party observability tools
- Modal integration
- KitchenAI Cloud integration
- DeepEval support
- NATS Message Broker integration

COMING SOON: A guide to building integrated Django apps as plugins.

---

## 🛡️ **Middleware Customization**

Decorated functions in KitchenAI are wrapped in middleware for pre- and post-processing. 

COMING SOON: Middleware configuration for developers to inject custom logic before and after function execution.

---

## 📄 **SDK Parser: Handling Unstructured Data**

KitchenAI includes a default **LlamaIndex Parser** to process unstructured data into documents.

### ✨ Example: Using the Parser
```python
from kitchenai.contrib.kitchenai_sdk.storage.llama_parser import Parser

parser = Parser(api_key=os.environ.get("LLAMA_CLOUD_API_KEY", None))
```

📢 **Note**: Files over 150MB automatically leverage the `LLAMA_CLOUD_API_KEY` for parsing.

---

## 🗄️ **Native PGVector Support** *(Coming Soon)*

KitchenAI will soon expose **pgvector** in its SDK to reuse Django database connections for vector storage.

---

## ⚙️ **Custom Configuration** *(Coming Soon)*

A guide on configuring KitchenAI through `settings.py` will soon be available.

---

## 🔒 **Authentication**

KitchenAI uses **Django-Allauth** for authentication, providing a flexible way to manage users.

### ✨ Upcoming:
- Custom auth backends
- A comprehensive guide for customizing KitchenAI authentication.

For now, refer to the [Django Ninja Authentication Docs](https://django-ninja.dev/).

---

## 👀 **Observability**

KitchenAI supports **Sentry** and **OpenTelemetry** for monitoring and error tracking.

🔮 COMING SOON:
- A guide on customizing observability.
- Support for more observability tools.

---

KitchenAI empowers you to focus on **building AI-driven features** by handling the boilerplate for you. Happy coding! 🎉