# 🤝 App Developers: Unlock AI for Your Applications  

As an **App Developer**, your role is to integrate AI capabilities seamlessly into your applications using the **KitchenAI Client SDK**. KitchenAI simplifies this process by providing standardized tools and abstractions, allowing you to focus on building amazing user experiences.

---

## 🌐 **API Overview**  

KitchenAI makes API interactions seamless, with comprehensive documentation available at `/api/docs`.  

### 🛠️ **API Documentation**  
Explore your API endpoints and interact with them directly from the automatically generated OpenAPI docs:  

![](../../_static/images/api-file.png)  

---

### **How It Works**  

KitchenAI uses metadata-driven routing to manage API requests. Here’s how:  

- **Metadata Handling**: Metadata in API requests is passed to the handler function to:  
  - Store data in the vector database.  
  - Retrieve data using metadata filters.  

- **`ingest_label`**:  
  - A crucial input parameter present across all endpoints.  
  - Directly maps the request to the labeled function you defined in your app.  
  - If the label doesn’t exist, a `404` is returned—**except for file uploads**, which are processed and stored by Django automatically.  

---

### **Key Features**  

- **Dynamic Routing**: KitchenAI intelligently routes requests based on `ingest_label`.  
- **Unified API Management**: All your AI functions are accessible and manageable from a single interface.  
- **Seamless File Handling**: File uploads are efficiently managed by Django.  

---



## 📦 **KitchenAI Client SDK**  

The **KitchenAI Client SDK** ensures a consistent and simple interface for interacting with LLM backends. It abstracts away the complexities of the framework backend, offering a **unified experience** across various languages and techniques.

### 🔜 **Coming Soon: Client SDKs**  
- 🐍 **Python SDK**  
- 🌐 **JavaScript SDK**  
- 🐹 **Go SDK**  
- 🦀 **Rust SDK**  

Python SDK:
 ```bash
 pip install kitchenai_python_sdk
 ```

[KitchenAI Python SDK](https://github.com/epuerta9/kitchenai-python-sdk)

No matter what framework or AI technique you’re using, KitchenAI's SDKs will enable:
- Unified interaction with the LLM backend.  
- Easy-to-use APIs tailored for your preferred language.  
- Seamless integration into your existing workflows.  

---

KitchenAI is designed to empower app developers by bridging the gap between **framework complexities** and **AI innovation**, making it simple to bring AI-driven features to your users. 🎯