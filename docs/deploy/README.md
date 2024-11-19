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