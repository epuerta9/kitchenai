# KitchenAI

<p align="center">
  <img src="docs/_static/images/logo.png" alt="KitchenAI" width="100" height="100">
</p>

**KitchenAI** is a control plane for AI implementations — designed to bridge the gap between application developers and AI teams. Our platform simplifies AI integration with a loosely coupled, modular architecture that delivers production-grade reliability while letting your teams focus on what they do best.

---

## 🚀 Quick Start

- **Explore Our Interactive Playground:**  
  [Try KitchenAI in Action](https://playground.kitchenai.dev/apps/playground)
- **Take a Guided Tour:**  
  [Watch the Guided Tour](https://app.arcade.software/share/j5ORenX65H5xuZWRppR4)

---

## 🌟 What Makes KitchenAI Unique

### Modular Architecture
- **Bento Boxes:** Package your AI workflows into independent "bento boxes" that encapsulate complex logic.  
- **Flexibility:** Update, replace, or scale individual modules without disrupting your overall system.  
- **Clear Separation:** Let AI teams build advanced logic in a reproducible and swappable space, while app developers enjoy a simple, stable API.

### High-Performance Messaging
- **Powered by NATS:**  
  - Lightning-fast, reliable communication between AI modules  
  - Dynamic service discovery and routing  
  - Robust support for event-driven workflows in distributed environments

### Framework Agnostic
- **Plug & Play:**  
  - No vendor lock-in—integrate with any AI framework or model  
  - Native support for LangChain, LlamaIndex, and custom implementations  
  - Future-proof your AI infrastructure with flexible integration options

---

## 🛠️ How It Works

KitchenAI’s three-layer architecture makes it easy to manage your AI workflows:

1. **Application Layer:**  
   Your business applications call a simple, unified API (just like using OpenAI’s Chat Completions).
   
2. **NATS Messaging Layer:**  
   This is our high-performance backbone for routing messages and discovering services dynamically.
   
3. **Bento Boxes Layer:**  
   Modular AI implementations where your AI team builds the complex logic (be it LLM logic, RAG, agents, or custom workflows).

### For Application Developers
Your code remains clean and simple:

```python
    # Simple integration using OpenAI's Chat Completions
    response = await openai_client.chat.completions.create(
        model="@llama-index-agents/query", #your bento box client id 
        messages=[{"role": "user", "content": data.query}]
    )
```

### For AI Teams
Focus on building powerful AI code:

```python
@kitchen.query.handler("query")
async def query_handler(data: WhiskQuerySchema) -> WhiskQueryBaseResponseSchema:
    # Advanced RAG implementation with best practices built-in
    index = VectorStoreIndex.from_vector_store(vector_store)
    query_engine = index.as_query_engine(
        chat_mode="best",
        filters=filters,
        llm=llm,
        verbose=True
    )
```

---
## Self hosting the control plane 

KitchenAI is designed to be self-hosted. You can deploy the control plane and the bento boxes separately.



1. Clone the KitchenAI repository
```bash
git clone https://github.com/epuerta9/kitchenai.git
```

2. Bring up the control plane and dependencies
```bash
docker compose up -d
```

4. Creating the Bucket for media. KitchenAI uses S3 for media. For local development, the compose file has a minio container. This only needs to be done the first time. 

you will need to login to the minio container and create a bucket called `kitchenai`.

endpoint: http://localhost:9001
username: minioadmin
password: minioadmin

bucket name: kitchenai

3. Bring up the bento boxes using this demo [demo notebooks](https://github.com/epuerta9/kitchenai-demo)
---

## Settings

available environment variables
```
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      DEBUG: "False"
      KITCHENAI_LOCAL: "False"
      KITCHENAI_LICENSE: "oss"
      ALLOWED_HOSTS: "*"
      CSRF_TRUSTED_ORIGINS: ""
      CACHE_LOCATION: ""
      KITCHENAI_REDIS_CACHE: "False"
      REDIS_LOCATION: "redis://127.0.0.1:6379/1"
      DATABASE_URL: "postgres://postgres:postgres@postgres:5432/postgres"
      CONN_MAX_AGE: "60"
      DEFAULT_FROM_EMAIL: "example@example.com"
      SECRET_KEY: "django-insecure-ef6nIh7LcUjPtixFdz0_aXyUwlKqvBdJEcycRR6RvRY"
      MEDIA_ROOT: "./media"
      SECURE_HSTS_SECONDS: "120"
      SECURE_HSTS_INCLUDE_SUBDOMAINS: "True"
      SECURE_HSTS_PRELOAD: "True"
      SESSION_COOKIE_SECURE: "True"
      SERVER_EMAIL: "example@example.com"
      AWS_ACCESS_KEY_ID: "minioadmin"
      AWS_SECRET_ACCESS_KEY: "minioadmin"
      AWS_STORAGE_BUCKET_NAME: "kitchenai"
      AWS_S3_ENDPOINT_URL: "http://minio:9000"
      AWS_DEFAULT_REGION: "us-east-1"
      AWS_S3_ADDRESSING_STYLE: "path"
      AWS_S3_USE_SSL: "True"
      AWS_S3_VERIFY: "True"
      USE_S3: "False"
      DJANGO_ALLOW_REGISTRATION: "True"
      RESEND_API_KEY: ""
      ADMIN_URL: "kitchenai-admin/"
      KITCHENAI_LLM_PROVIDER: "openai"
      KITCHENAI_LLM_MODEL: "gpt-4o"
      KITCHENAI_AUTH: "False"
      KITCHENAI_JWT_SECRET: ""
      WHISK_USER: "kitchenai"
      WHISK_PASSWORD: "kitchenai_admin"
      NATS_URL: "nats://nats:4222"
      KITCHENAI_THEME: "winter"
      MEDIA_BASE_URL: "http://localhost:8080"
```


## 📚 Documentation

- [Getting Started](https://kitchenai.dev/docs/getting-started)
- [Core Concepts](https://kitchenai.dev/docs/core-concepts)
- [Deployment Guide](https://kitchenai.dev/docs/deployment)
- [API Reference](https://kitchenai.dev/docs/api-reference)

---

## 🛠️ Key Features

- **Version Control & Rollback:** Safely iterate and revert as needed.
- **Monitoring & Observability Hooks:** Integrate with your favorite tools.
- **Plugin Ecosystem:** Extend KitchenAI with additional capabilities.
- **Security Integrations:** Designed with production-grade best practices.

---

## 🙋‍♂️ Join the Beta!

KitchenAI is still in beta—we're excited to have early adopters help shape the platform.  
- **Join the Waitlist:** [Get Early Access](https://kitchenai.dev/#waitlist)  
- **Play in Our Playground:** [Try it out now](https://playground.kitchenai.dev)

---

## 🔗 Quick Links

- [Website](https://kitchenai.dev)
- [Documentation](https://kitchenai.dev/docs)
- [Interactive Playground](https://playground.kitchenai.dev)
- [GitHub](https://github.com/epuerta9/kitchenai)

---

## 📄 License

KitchenAI is released under the [Apache 2.0 License](LICENSE).

---

## 🙋‍♂️ Support & Community

- [Community Forum](https://kitchenai.dev/community)
- [GitHub Issues](https://github.com/epuerta9/kitchenai/issues)
- [Email Support](mailto:support@kitchenai.dev)

---

<p align="center">
  Built with ❤️ by the KitchenAI Team
</p>
