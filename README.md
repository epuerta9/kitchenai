<p align="center">
  <img src="docs/_static/images/logo.png" alt="KitchenAI" width="100" height="100">
</p>

# **KitchenAI: Integrate Advanced AI Implementations in Minutes**  
**Simplify AI Development with KitchenAI: Your AI Backend and LLMOps Toolkit**  

[![Docs](https://img.shields.io/badge/Docs-kitchenai.dev-blue)](https://docs.kitchenai.dev)  
[![Falco](https://img.shields.io/badge/built%20with-falco-success)](https://github.com/Tobi-De/falco)  
[![Hatch Project](https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg)](https://github.com/pypa/hatch)  

---


## 🚀 **What is KitchenAI?**  

**KitchenAI** is an **open-source AI runtime and backend** that streamlines **complex AI agent** workflows. We provide a **plug-and-play** suite of **Bento Box** AI implementations (e.g., specialized “Sales Agency,” “TrendSpotter,” “Document Summarizer,” etc.)—all **pre-optimized** for popular use cases. 



**Our vision**: Let you seamlessly **drop** these Bento Boxes into your application so you can focus on **delivering value** rather than reinventing AI pipelines or infrastructure.

### **Why KitchenAI?**  

- **Fastest Path to AI Orchestration**  
  - Tap into **multi-step agent workflows** (RAG, LLM calls, prompt engineering) **without** writing a custom backend.  
  - One-click install with **Docker Compose**—run in minutes.

- **Developer-First & Open Source**  
  - Everything is **source-available** for easy integration and customization.  
  - A **modular** approach ensures you pick only the AI “Bento Boxes” you need.

- **Business Value**  
  - Shorten time to market for advanced AI features.  
  - Enterprise-friendly: self-host in secure environments, tailor to internal data.

---

## 🛠️ **Who Uses KitchenAI?**  

- **Product Teams & Devs** who want to embed **agent-based AI** flows (e.g., writing marketing copy, analyzing data, generating insights) without building everything from scratch.  
- **Data Scientists** transitioning prototypes to **production** quickly—KitchenAI’s built-in LLMOps ensures easy debugging and logging.  
- **Enterprises** seeking a **private** or **on-prem** AI solution that’s easily auditable and **secure**.

---

## 💡 **Example Use Case: TrendSpotter Bento (API-Driven AI Agents)**  

The **TrendSpotter Bento** simplifies complex **AI agent orchestration** into a streamlined **API-first** experience, empowering developers to focus on **value delivery** instead of backend complexity.

### **How It Works:**
1. **Spin Up with One Click:**  
   - Run **KitchenAI** with a pre-configured **Docker Compose** file.  
   - The TrendSpotter Bento Box launches pre-optimized **agent skills** like RAG (Retrieval-Augmented Generation), summarization, and email delivery.

2. **Agent with Optimized Skills Out-of-the-Box:**  
   - The agent is **pre-configured** for a domain-specific use case (trend detection).  
   - Fully optimized for **RAG queries**, **summarization**, and **data filtering**.  

3. **Developer APIs for Custom Knowledge & RAG Integration:**  
   - Developers have complete control over **customizing** knowledge bases and retrieval behavior.  
   - Use the `/embed` and `/file` endpoints to **upload data** and **apply metadata filters** to **tailor** the agent’s responses to your application's context.  
   - **Example:** Upload reports, articles, or proprietary datasets and query them using structured metadata.

4. **Flexible Query Handling:**  
   - Send a query directly to the **agent API**:  
     ```bash
     curl -X POST http://localhost:8000/agent/trendspotter/query \
          -H "Content-Type: application/json" \
          -d '{"query": "Find the latest climate trends"}'
     ```
   - Use **metadata filters** for precision control:  
     ```bash
     curl -X POST http://localhost:8000/agent/trendspotter/query \
          -H "Content-Type: application/json" \
          -d '{"query": "Find trends in renewable energy", "filters": {"topic": "climate", "region": "US"}}'
     ```

5. **Zero-Code Workflow Management:**  
   - **No need for multi-step workflow coding.**  
   - The **agent API** abstracts complex **Temporal workflows** behind a single endpoint.  
   - **Durable** execution with support for **multiple agents**, **event streaming**, and **human-in-the-loop interactions.**

---

### ✅ **Why This Approach Works:**
- **API-First Agent Experience:** No need to build custom workflows—just send queries via HTTP.  
- **Fully Customizable RAG:** Use the `/file` and `/embed` endpoints to add domain-specific data with **metadata filters.**  
- **Rapid Developer Integration:** No complex orchestration logic—**focus on your data and questions.**  
- **Immediate Value:** Spin up a **production-ready AI agent** in minutes with minimal setup.  

---


## 🚀 **Getting Started (One-Click Docker Compose)**  

1. **Clone** or **download** the KitchenAI repo (or a sample docker-compose.yml).  
2. **Launch** with:
   ```bash
   docker compose up -d
   ```
3. Once running, go to `http://localhost:8001/api/v1/agent/<bento_name>/query` (or see the docs).  
4. Start making requests—KitchenAI handles the multi-step agent workflows automatically.

**Within minutes**, you have a **full AI runtime** exposed as HTTP endpoints, with out-of-the-box Bento Boxes covering common AI tasks like summarization, trend analysis, or Q&A.

---

## 🧩 **An Array of Bento Boxes**  

**KitchenAI** ships with pre-built Bento Boxes, each **optimized** for a particular domain:

- **Sales Agency** – Generate leads, craft follow-ups, sync with CRMs.  
- **TrendSpotter** – Grab social or news data, do real-time RAG, produce insights.  
- **Document Summarizer** – Summarize PDFs, docs, or knowledge bases.  
- **(More Coming Soon)** – Seamless GPT-based chat flows, classification, image generation, etc.

You just **enable** them in a config or pass an environment variable, then your app can call:

```
POST /agent/<bento_label>/query
{
  "query": "Analyze these docs and give me the top 3 insights."
}
```

---


Here's an enhanced version of your **"How It Works"** section with the **LLMOps infrastructure** focus included:

---

## **How It Works: AI Workflows with Built-In LLMOps**  

**KitchenAI** is not just a runtime—it's a **complete AI orchestration platform** built for **production-ready** workflows with **LLMOps** baked in from the ground up.

### **AI Agent Workflow Architecture**  
1. **Bento Box Integration:**  
   - Each **Bento Box** is a pre-optimized AI implementation containing specialized agent workflows (e.g., Sales Agency, TrendSpotter).  
   - Bento Boxes expose **standardized API endpoints** for direct use, so you can run complex AI processes with a simple REST call.

2. **Intelligent Workflow Management:**  
   - **Temporal.io** powers **durable, long-running workflows** with built-in fault tolerance and retry mechanisms.  
   - **KitchenAI’s ProjectManager Workflow** dynamically selects the right **Agent Tools** and **Skills** for the user’s query.  
   - **Multi-agent collaboration**: One query can trigger multiple **agent skills** working in parallel or sequentially.

3. **Built-in RAG & Prompt Management:**  
   - **RAG (Retrieval-Augmented Generation)** with customizable **metadata filtering**.  
   - **Prompt Management & Query Modifiers:** Easily adjust how prompts are constructed using **configurable modifiers**.  
   - **Response Synthesizers:** Control how AI outputs are processed, summarized, or merged for final delivery.

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

---

### **Observability-Ready by Default:**
**No extra setup required**—KitchenAI **automatically** wires in:  
- ✅ **LLM Call Logging & Performance Metrics**  
- ✅ **Agent Tool Usage Analytics**  
- ✅ **Token Usage & Cost Reporting**  

---

### **Developer Experience Example:**
1. **Install and Launch:**  
   ```bash
   docker compose up -d
   ```
2. **Send a Query:**  
   ```bash
   curl -X POST http://localhost:8000/agent/trendspotter/query \
        -H "Content-Type: application/json" \
        -d '{"query": "Find the latest climate trends"}'
   ```
3. **Monitor Performance:**  
   - View **real-time traces** in **Grafana** at `http://localhost:3000`.  
   - Check **AI accuracy metrics** in **DeepEval**.  
   - Capture errors in **Sentry** if something fails.  

---

## **Why This Matters for You:**  

- ✅ **No Extra Setup:** LLMOps tools are **pre-configured**. Just **run KitchenAI**, and **start monitoring**.  
- ✅ **Insights for Developers:** Gain **deep visibility** into how AI agents behave across **skills and tools**.  
- ✅ **Enterprise-Ready:** All **monitoring tools** can be **self-hosted** or **integrated** with existing observability stacks.  

---

## **Coming Soon: Build Your Own Bento Boxes!**  
- **Developer Flow:** KitchenAI will soon allow **custom Bento Boxes** where developers can define their own:  
   - **Agent Skills & Tools**  
   - **Custom RAG Pipelines**  
   - **Temporal Workflows**  
- **Self-Host Anywhere:** Easily build **your own KitchenAI image** with your own **data privacy** policies.  

---

KitchenAI: **Production-Ready AI Workflows, Built for Developers.**  
👉 **Try it Today with One-Click Docker Compose Setup!**

---

## 🤝 **Contribute & Community**  

- **Star** us on GitHub—help grow the project!  
- **Open issues** or **pull requests** for new Bento Boxes or bugfixes.  
- Join the **KitchenAI** community calls to share feedback and suggestions.


---

**Get Started** today with a single `docker compose up`—then watch **KitchenAI** handle your advanced AI agents so **you** can focus on delivering product value to **your** users.