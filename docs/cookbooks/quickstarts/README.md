# 📚 Quickstarts  

Quickstarts are your recipes to quickly get up and running with **KitchenAI**. Follow these simple steps to get started, whether you're building with the **llama-index starter** or another project.  

---

## 🏗️ **Anatomy of a KitchenAI App**  
Every KitchenAI app starts with two essential files:  
- **`app.py`**: Your application logic.  
- **`requirements.txt`**: Your dependencies.  

> 🔜 **Coming Soon**: Support for structured application packages instead of just a single `app.py` file.  

---

## 🐾 **Quickstart with Llama-Index Starter**  

### 1️⃣ **Export Your OpenAI API Key**  
KitchenAI uses OpenAI as the default LLM provider. Set your key in the environment:  

```bash
export OPENAI_API_KEY=<your-key>
export KITCHENAI_DEBUG=True
```  

> 🌟 _You can swap OpenAI for other providers as needed!_  

---

### 2️⃣ **Install KitchenAI**  

Set up a virtual environment and install KitchenAI:  

```bash
python -m venv venv && source venv/bin/activate &&  pip install kitchenai
```  

---

### 3️⃣ **Browse and Select Projects**  

List and select a starter project, such as the **llama-index starter**:  

```bash
kitchenai cook list && kitchenai cook select llama-index-starter && pip install -r requirements.txt
```  

📸 _List available projects:_  
![](../../_static/images/kitchenai-list.gif)  

---

### 4️⃣ **Initialize the Environment**  

Run the following commands to initialize and start your KitchenAI server:  

```bash
kitchenai init && kitchenai dev --module app:kitchen
```  

📸 _Spin up your API server in seconds:_  
![](../../_static/images/kitchenai-dev.gif)  

📸 _Explore your auto-generated OpenAPI docs:_  
![](../../_static/images/openapi.png)  

---

### 5️⃣ **Build a Docker Container**  

Package your application into a Docker container:  

```bash
kitchenai build . app:kitchenai
```  

📸 _Effortlessly containerize your application:_  
![](../../_static/images/kitchenai-build.gif)  

Your container will be named **`kitchenai-app`**.  

---

## 📝 **Next Steps**  

- [Deploy Your App](../../deploy/README.md)  
