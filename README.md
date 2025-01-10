# 🍽️ **KitchenAI**  

<p align="center">
  <img src="docs/_static/images/logo.png" alt="KitchenAI" width="100" height="100">
</p>

**Simplify AI Development with KitchenAI: Your AI Backend and LLMOps Toolkit**  

[![Docs](https://img.shields.io/badge/Docs-kitchenai.dev-blue)](https://docs.kitchenai.dev)  
[![Falco](https://img.shields.io/badge/built%20with-falco-success)](https://github.com/Tobi-De/falco)  
[![Hatch Project](https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg)](https://github.com/pypa/hatch)  

---

**[Documentation](https://docs.kitchenai.dev)**
**[KitchenAI Cloud](#-get-early-access)**

## 🚀 **What is KitchenAI?**  

KitchenAI is an open-source toolkit that simplifies AI complexities by acting as your **AI backend** and **LLMOps solution**—from experimentation to production.  

It empowers **developers** to focus on delivering results without getting stuck in the weeds of AI infrastructure, observability, or deployment.  

### **Key Goals**:  
1. **Simplify AI Integration**: Easily turn AI experiments into production-ready APIs.  
2. **Provide an AI Backend**: Handle the entire AI lifecycle—experimentation, observability, and scaling.  
3. **Empower Developers**: Focus on application building, not infrastructure.

![kitchenai-dev](docs/_static/images/kitchenai-highlevel1.png)

---

## 🛠️ **Who is KitchenAI For?**  

- **Application Developers**:  
   - Seamlessly integrate AI into your apps using APIs.  
   - Experiment and test AI techniques without reinventing the wheel.  

- **AI Developers & Data Scientists**:  
   - Move quickly from Jupyter notebooks to production-ready services.  
   - Deploy custom AI techniques with ease (e.g., RAG, embeddings).  

- **Platform & Infra Engineers**:  
   - Customize your AI stack, integrate tools like Sentry, OpenTelemetry, and more.  
   - Scale and optimize AI services with a modular, extensible framework.  

---
**Say goodbye to boilerplate!**  

## 🚀 **Go from notebook to app integration in minutes.**
Example notebook: [kitchenai-community/llama_index_starter](https://github.com/epuerta9/kitchenai-community/blob/main/src/kitchenai_community/llama_index_starter/notebook.ipynb)

By annotating your notebook with KitchenAI annotations, you can go from this:

![kitchenai-dev](docs/_static/images/jupyter-notebook.png)

To interacting with the API using the built in client:

![kitchenai-dev](docs/_static/images/cli-query.png)

---

## 💡 **Why KitchenAI?**  

Integrating and scaling AI is **too complex** today. KitchenAI solves this:  

1. **AI Backend Ready to Go**:  
   - Stop building APIs and infra from scratch. Deploy AI code as production-ready APIs in minutes.  

2. **Built-In LLMOps Features**:  
   - Observability, tracing, and evaluation tools are pre-configured.  

3. **Framework-Agnostic & Extensible**:  
   - Vendor-neutral, open-source, and easy to customize with plugins.  

4. **Faster Time-to-Production**:  
   - Go from experimentation to live deployments seamlessly.  

---

## ⚡ **Quickstart**  

1. **Set Up Environment**  
   ```bash
   export OPENAI_API_KEY=<your key>
   export KITCHENAI_DEBUG=True
   python -m venv venv && source venv/bin/activate && pip install kitchenai
   ```

2. **Start a Project**  
   ```bash
   kitchenai cook list && kitchenai cook select llama-index-chat && pip install -r requirements.txt
   ```
   ![kitchenai-list](docs/_static/images/kitchenai-list.gif)
   

3. **Run the Server**  
   ```bash
   kitchenai init && kitchenai dev --module app:kitchen
   ```
   Alternatively, you can run the server with jupyter notebook:
   ```bash
   kitchenai dev --module app:kitchen --jupyter
   ```

4. **Test the API**  
   ```bash
   kitchenai client health
   ```
   ```bash
   kitchenai client labels
   ```
   ![kitchenai-client](docs/_static/images/kitchenai-dev-client.gif)


5. **Build Docker Container**  
   ```bash
   kitchenai build . app:kitchenai
   ```  

📖 Full quickstart guide at [docs.kitchenai.dev](https://docs.kitchenai.dev/cookbooks/quickstarts/).  

---

## ✨ **Features**  

- **🚀 Production-Ready Backend**: Go from idea to production in minutes.  
- **🛠️ Built-In LLMOps**: Observability, tracing, and evaluation out-of-the-box.  
- **🔌 Extensible Framework**: Easily add custom plugins and AI techniques.  
- **📦 Modular AI Modules**: Deploy and test AI components with ease.  
- **🐳 Docker-First Deployment**: Build and scale with confidence.  

---


## 📊 **AI Lifecycle with KitchenAI**  

1. **Experiment**:  
   - Start in Jupyter notebooks or existing AI tools.  
   - Annotate your notebook to turn it into a deployable AI module.  

2. **Build**:  
   - Use KitchenAI to generate production-ready APIs automatically.  

3. **Deploy**:  
   - Run the module locally or in production with built-in observability and scaling.  

4. **Monitor & Improve**:  
   - Use KitchenAI's observability tools to evaluate performance, trace issues, and iterate.  

## Developer Experience


![Developer Flow](docs/_static/images/workflow.png)

---

## 🔧 **Under the Hood**  

- **Django Ninja**: High-performance async APIs.  
- **LLMOps Stack**: Built-in tracing, observability, and evaluations.  
- **Plugin System**: Add advanced custom functionality.  
- **Docker-Optimized**: Seamless deployment with S6 overlays.  

---

## 🚀 **KitchenAI Cloud**  

Coming soon: **KitchenAI Cloud** will offer a fully managed AI backend experience.  

### **Key Benefits**:  
- Serverless deployment for AI modules.  
- Fully managed observability, tracing, and scaling.  
- Team collaboration tools for faster iteration.  

🔗 **Sign Up for Early Access**: [Register Here](https://tally.so/r/w8pYoo)  

---

## 🛠️ **Roadmap**  

- Expanded SDKs (Python, Go, JS).  
- Enhanced plugin system.  
- Enterprise-grade observability features.  
- KitchenAI Cloud Beta.  

---

## 🤝 **Contribute**  

Kitchenai is in **alpha-**


We’re building KitchenAI in the open, and we’d love your contributions:  
- ⭐ Star the repo on GitHub!  
- 🛠️ Submit PRs, ideas, or feedback.  
- 🧑‍🍳 Build plugins and AI modules for the community.  

---

## 🙏 **Acknowledgements**  

KitchenAI is inspired by the open-source community and modern AI development challenges. Let’s simplify AI, together.  

Notable project: [Falco Project](https://github.com/Tobi-De/falco). Thanks to the Python community for best practices and tools!  

---

## 📊 **Telemetry**  

KitchenAI collects **anonymous usage data** to improve the framework—no PII or sensitive data is collected.  

> Your feedback and support shape KitchenAI. Let's build the future of AI development together!  

## 🔧 **Quick Install**

You can quickly install KitchenAI Development Kit using this one-liner:


`/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/epuerta9/kitchenai/main/scripts/install.sh)"`


You can also install the bundle with docker and docker-compose:

`curl -sSL https://raw.githubusercontent.com/epuerta9/kitchenai/main/scripts/install-bundle.sh | bash`
