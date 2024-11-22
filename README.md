

# 🍽️ KitchenAI  

<p align="center">
  <img src="docs/_static/images/logo.png" alt="KitchenAI" width="100" height="100">
</p>

**Instantly turn AI code into a production-ready backend.**  

[![Falco](https://img.shields.io/badge/built%20with-falco-success)](https://github.com/Tobi-De/falco)  
[![Hatch Project](https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg)](https://github.com/pypa/hatch)  
[![Docs](https://img.shields.io/badge/Docs-kitchenai.dev-blue)](https://docs.kitchenai.dev)

---




## **What is KitchenAI?**  
KitchenAI bridges the gap between **AI developers**, **application developers**, and **Infrastructure developers** making it easy to:  

- For **AI Developers**: Focus on your techniques like RAG or embeddings—KitchenAI handles scalable, production-ready features through ecosystem building blocks.  
- For **App Developers**: Seamlessly integrate AI with open-source APIs and robust backends built on Django.

- For **Infrastructure Developers**: Integrate seamlessly with AI tooling, customize Django backends, and leverage built-in support for observability platforms like Sentry and OpenTelemetry, ensuring scalable and production-ready deployments with tools like Docker and Kubernetes.  

**Say goodbye to boilerplate!**  


[Documentation](https://docs.kitchenai.dev)

![kitchenai-list](docs/_static/images/kitchenai-list.gif)

---

## 🚀 **Why KitchenAI?**  

Building AI applications often requires juggling complex frameworks and backend systems. KitchenAI eliminates that complexity by:  

- Turning AI functions into APIs automatically.  
- Offering a **production-ready server** using **proven technologies** like Django, Django Ninja, an extensible plugin framework, background workers, and AI third party integrations.  
- Enabling extensibility while maintaining simplicity.  

🔗 Learn more at [docs.kitchenai.dev](https://docs.kitchenai.dev/develop/).  

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

   ![kitchenai-dev](docs/_static/images/kitchenai-dev.gif)

   An entire API server is spun up in seconds.

   ![openapi](docs/_static/images/openapi.png)


4. **Build Docker Container**  
   ```bash
   kitchenai build . app:kitchenai
   ```  

📖 Full quickstart guide at [docs.kitchenai.dev](https://docs.kitchenai.dev/cookbooks/quickstarts/).  

---

## ✨ **Features**  

- **📦 Quick Cookbook Creation**: Build cookbooks in seconds.  
- **🚀 Production-Ready AI**: Turn AI code into robust endpoints.  
- **🔌 Extensible Framework**: Add custom recipes and plugins effortlessly.  
- **🐳 Docker-First Deployment**: Deploy with ease.  

---

## 🔧 **Under the Hood**  

- **Django Ninja**: Async-first API framework for high-performance endpoints.  
- **Django Q2**: Background workers for long-running tasks. 
- **Plugin Framework**: Django DJP integration
- **AI Ecosystem**: Integrations to AI ecosystem and tools 
- **S6 Overlay**: Optimized container orchestration.  

KitchenAI is **built for developers**, offering flexibility and scalability while letting you focus on AI.

---

## Developer Experience

![Developer Flow](docs/_static/images/developer-flow.png)



## 🛠️ **Roadmap**  

- **SDKs** for Python, Go, JS, and Rust.  
- Enhanced plugin system.  
- Signal-based architecture for event-driven apps.  
- Built-in support for **Postgres** and **pgvector**.  

---

## 🧑‍🍳 **Contribute**  

KitchenAI is in **alpha**—we welcome your contributions and feedback!  


---

## 🙏 **Acknowledgements**  

Inspired by the [Falco Project](https://github.com/Tobi-De/falco). Thanks to the Python community for best practices and tools!  

---

## 📊 **Telemetry**  

KitchenAI collects **anonymous usage data** to improve the framework—no PII or sensitive data is collected.  

> Your feedback and support shape KitchenAI. Let's build the future of AI development together!  