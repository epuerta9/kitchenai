
---
# 🍽️ KitchenAI

[![Falco](https://img.shields.io/badge/built%20with-falco-success)](https://github.com/Tobi-De/falco)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Hatch Project](https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg)](https://github.com/pypa/hatch)

**Your AI Kitchen Assistant for Production-Ready Cookbooks!**

KitchenAI is designed to make building, sharing, and consuming AI-powered cookbooks easy, efficient, and scalable. Whether you want to quickly prototype AI solutions or deploy robust applications, KitchenAI provides the tools you need—all in one place!

## 🚀 Features
- **Quick Cookbook Creation**: Spin up new cookbooks with one command.
- **Production-Ready AI**: Turn your ideas into robust, AI-driven endpoints.
- **Extensible Framework**: Easily add your custom recipes and integrate them into your apps.
- **Containerized Deployment**: Build Docker containers and share your cookbooks effortlessly.

---

## 📋 Prerequisites

Before you start, make sure you have the following:

- Python `3.11+`
- [Hatch 1.9.1+](https://hatch.pypa.io/latest/)
- [Just](https://github.com/casey/just) task runner

---

## ⚡ Quickstart

### Step 1: Export Your OpenAI API Key

KitchenAI’s demo uses OpenAI as the LLM provider. Set your OpenAI key in your environment:

```bash
export OPENAI_API_KEY=<your key>
```

> _Feel free to customize this with other LLM providers as needed!_

### Step 2: Install KitchenAI

Install the application globally using `pipx`:

```bash
pipx install kitchenai
```

### Step 3: Create a New Cookbook

```bash
kitchenai new
```

Cookbooks are prefixed with `kitchenai_<project_name>` for easy identification and organization.

### Step 4: Bootstrap Your Development Environment

```bash
just bootstrap
```

This sets up Python environments using Hatch:
- `default` environment
- `dev` environment for active development

### Step 5: Enter Your Development Environment

```bash
hatch shell dev
```

This is equivalent to activating a virtual environment (`source venv/bin/activate`)—but better!

### Step 6: Initialize Your Cookbook

```bash
kitchenai init
```

KitchenAI reads your `kitchenai.yml` file and stores the metadata locally in an SQLite database, readying your project for execution.

### Step 7: Run Your Cookbook

```bash
kitchenai dev
```

This command imports your cookbook module and transforms your functions into production-ready endpoints, adhering to best practices.

---

## 🛠️ Building and Sharing

Ready to share your AI magic with the world? KitchenAI makes it simple to package and deploy your cookbooks!

### Step 1: Build a Python Wheel

```bash
hatch build
```

This creates a distributable `.whl` package, ready for publishing to PyPI.

### Step 2: Build a Docker Container

```bash
hatch run docker-build
```

With these two commands, you can quickly prepare your AI solutions for deployment and distribution!

---

## 🐳 Running Docker Compose

Once your image is built, you can run it with Docker Compose. Add any dependencies your cookbook requires, and spin up your environment:

```bash
docker compose up -d
```

### 💡 Tip:
Add any necessary dependency containers to fit your specific use case and requirements!

---

## 🧑‍🍳 Project Setup

Make sure the Python version in your `.pre-commit-config.yaml` file matches the version in your virtual environment. If you need to manage Python installations, Hatch has you covered: [Managing Python with Hatch](https://hatch.pypa.io/latest/tutorials/python/manage/).

To set up your project:

```bash
just setup
```

This command sets up your virtual environment, installs dependencies, runs migrations, and creates a superuser (`admin@localhost` with password `admin`).

### Running the Django Development Server

```bash
just server
```

This launches the Django development server, making it easy to test your application locally.

---

## 🙏 Acknowledgements

This project draws inspiration from the [Falco Project](https://github.com/Tobi-De/falco), and incorporates best practices and tools from across the Python ecosystem.

> 💡 **Pro Tip**: Run `just` to see all available commands and streamline your development workflow!

