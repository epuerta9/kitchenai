# 🚀 Deployment Options  

KitchenAI is currently in **alpha**, and production workloads are not fully supported yet. We're working hard to roll out support for production environments in the coming months.  

In the meantime, here’s how you can get started:  

---

## 🐳 **Docker Container**  

KitchenAI offers flexibility by supporting **Docker containers** as the primary deployment method.  

Easily build a container for your KitchenAI app with the CLI:  

```bash
kitchenai build . app:kitchen
```  

> Once built, the container can be deployed using **Docker Compose**, **Kubernetes**, or any other container orchestrator.  

📸 **Example:**  

![kitchenai-build](../_static/images/kitchenai-build.gif)  

---

## 🐋 **Docker Compose**

KitchenAI provides a simple Docker Compose configuration for orchestrating your containers. Here's the basic `docker-compose.yml` file:


```
version: '3.8'
services:


  #for local development we don't need the image directly.Uncomment if you want to use the image you built and choose local as env
  kitchenai:
    image: kitchenai-app:latest
    container_name: kitchenai-app
    ports:
    - "8001:8001"
    network_mode: host
    env_file:
      - .env
    volumes:
      - chroma_db:/app/chroma_db
      - sqlite:/app/.kitchenai



volumes:
  chroma_db:
    driver: local
  sqlite:
    driver: local

```


## 📝 **Environment Variables**

KitchenAI uses a `.env` file to manage configuration. Here's a sample `.env` file with common settings:
```
KITCHENAI_DEBUG=True
OPENAI_API_KEY=<api key>
```


## 🗄️ **Databases**  

### **Default: Sqlite**  
By default, KitchenAI uses **Sqlite** for simple and lightweight storage.  

### **Coming Soon: Postgres**  
Postgres support is on the way to handle **production workloads** with scalability and reliability.  

### **Vector Database Support**  
KitchenAI supports **any vector database** out of the box.  

The examples in our documentation use **ChromaDB** with disk persistence, but feel free to integrate with your preferred vector store.  

---

Stay tuned for updates as we bring full production support to KitchenAI! 🔧