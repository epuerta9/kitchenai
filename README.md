# 🍽️ **KitchenAI**  

<p align="center">
  <img src="docs/_static/images/logo.png" alt="KitchenAI" width="100" height="100">
</p>

**Empower Your AI Development with KitchenAI: An AI Runtime for Experimentation, Integration, and Deployment**  

[![Docs](https://img.shields.io/badge/Docs-kitchenai.dev-blue)](https://docs.kitchenai.dev)  
[![Falco](https://img.shields.io/badge/built%20with-falco-success)](https://github.com/Tobi-De/falco)  
[![Hatch Project](https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg)](https://github.com/pypa/hatch)  

---

**[Documentation](https://docs.kitchenai.dev)**
**[KitchenAI Cloud](#-get-early-access)**

## 🚀 **What is KitchenAI?**  

KitchenAI is an open-source AI runtime designed to simplify experimentation, integration, and deployment for AI development teams. It transforms complex AI projects into scalable, distributed systems using lightweight, shareable AI components called Bento Boxes.

With KitchenAI, you can:

- **Experiment and test** AI techniques like RAG or embeddings effortlessly.
- **Integrate and deploy** distributed AI applications seamlessly.
- **Scale and unify** polyglot AI systems under one API.

### **Key Features**:  
1. **Distributed AI Runtime**: Build and scale AI systems with polyglot components.  
2. **Framework & Cloud Agnostic**: Use any AI framework or cloud platform.  
3. **Lightweight Bento Boxes**: Package and share AI implementations in minutes.


---

## 🛠️ **Who is KitchenAI For?**  

- **AI Development Teams**: Build, test, and deploy AI systems quickly without operational overhead.
- **Application Developers**: Simplify AI integration with unified APIs.
- **Data Scientists**: Deploy your experiments into production-ready services effortlessly.
- **Infrastructure Engineers**: Optimize distributed AI systems with modular components and observability tools.

---
**Say goodbye to complexity!**  

## 🚀 **Transform AI development with KitchenAI**
Example: Turn AI experiments into Bento Boxes and deploy distributed AI systems:  


---

## 💡 **Why KitchenAI?**  

KitchenAI eliminates the hurdles of AI development by offering:

1. **Unified AI Runtime**: Seamlessly integrate diverse frameworks, tools, and languages.  
2. **NATS-Powered Messaging Fabric**: Connect Bento Boxes to create distributed, scalable AI systems.  
3. **Plugin Ecosystem**: Extend capabilities with prompt management, evaluations, and more.  
4. **Vendor Neutral**: Keep your AI stack portable and flexible.  
5. **Faster Experimentation to Deployment**: Focus on innovation, not infrastructure.

---

## ⚡ **Quickstart**  

1. **Start the KitchenAI Control Plane**  
   ```bash
   export OPENAI_API_KEY=<your key>
   git clone https://github.com/epuerta9/kitchenai.git 
   docker compose up -d 
   ```

2. **Create a Local Account**  
    go to `http://localhost:8001` and create an account.
    ![kitchenai-dev](docs/_static/images/sign-in.png)

3. **Run the Example Bento Box**
    This will connect to the KitchenAI Control Plane and run the example bento box.
   ```bash
   uv run whisk/examples/query-example.py
   ```

4. **Make Your Own Bento Box**  


📖 Full quickstart guide at [docs.kitchenai.dev](https://docs.kitchenai.dev/cookbooks/quickstarts/).  

---

## ✨ **Features**  

- **🚀 Distributed AI Runtime**: Build AI systems with ease.  
- **🛠️ NATS Messaging Fabric**: Connect components for scalable, distributed workflows.  
- **🔌 Plugin Ecosystem**: Extend capabilities with custom integrations.  
- **📦 Bento Boxes**: Shareable, lightweight AI implementations.  
- **🌐 Framework & Cloud Agnostic**: Deploy anywhere, with any stack.  

---

## 📊 **AI Lifecycle with KitchenAI**  

1. **Experiment**: Develop AI techniques and annotate them for deployment.  
2. **Build**: Package techniques into Bento Boxes.  
3. **Deploy**: Run distributed systems with observability and scaling tools.  
4. **Iterate**: Improve using built-in performance and tracing features.  

---

## 🔧 **Under the Hood**  

- **NATS Messaging Fabric**: Seamless connectivity for distributed systems.  
- **Bento Boxes**: Lightweight, shareable AI components.  
- **Plugin System**: Extend with prompt management, evaluations, and more.  
- **Observability Built-In**: Tools for tracing, monitoring, and debugging.  

---

### **LLMOps Infrastructure (Baked In)**  

**Every KitchenAI instance includes a complete LLMOps suite for production visibility and control:**  

- **✅ OpenTelemetry Integration:** Full tracing across **workflows**, **agent calls**, and **vector stores**.  
- **✅ DeepEval Integration:** Real-time **AI performance evaluation**—track accuracy, relevance, and quality metrics out-of-the-box.  
- **✅ Grafana Dashboards:** Pre-configured **visual dashboards** for monitoring workflow health, latencies, and throughput.  
- **✅ Sentry Integration:** Capture **errors** and exceptions across your **entire AI stack**, from vector lookups to LLM responses.  
- **✅ Prompt Management:** Define reusable **prompt templates** with version control and easy debugging.  
- **✅ Query Modifiers:** Dynamically **transform** user queries before they reach the model for better results.  
- **✅ Response Synthesizer:** Ensure **consistent outputs** by applying customizable response transformations.  


## 🚀 **Roadmap**  

- Streaming support.
- Agent orchestration workflows.
- Advanced observability features.
- OpenAI API compatibility.
- Marimo integrations.

📣 **Have suggestions or want to contribute?** Reach out to join the KitchenAI journey!  

---

## 🤝 **Contribute**  

KitchenAI is open-source and thrives on community contributions:  
- ⭐ Star the repo on GitHub!  
- 🛠️ Submit PRs or share feedback.  
- 🧑‍🍳 Build plugins and share AI modules.

---

## 🙏 **Acknowledgements**  

KitchenAI draws inspiration from the open-source community and modern AI challenges. Together, we simplify AI development!  

---

## 📊 **Telemetry**  

KitchenAI collects **anonymous usage data** to improve the framework—no PII or sensitive data is collected.  

> Let’s build the future of AI development together!

