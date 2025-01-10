

# KitchenAI Development Kit

Welcome to the KitchenAI Development Kit! This guide will help you set up and explore the development environment for KitchenAI. Follow the steps below to get started.

## Getting Started

### Step 1: Set Up Your Environment

Before you begin, ensure you have your OpenAI API key ready. Export it into your environment with the following command:

````bash
export OPENAI_API_KEY=your-api-key-here
````

### Step 2: Launch the Development Environment

Run the following command to bring up the Docker Compose environment:

````bash
docker-compose up -d
````

This command will start a collection of containers. Please be patient, as it may take some time for all services to boot up.

### Step 3: Create a KitchenAI Bucket

Navigate to `localhost:9001` in your web browser and create a KitchenAI bucket. This step is essential for managing your data within the KitchenAI environment.

### Step 4: Connect with VSCode

Open your Visual Studio Code and connect to the KitchenAI development container named `kitchenai-local` using DevContainers. This connection allows you to work directly within the KitchenAI project, enabling you to make updates and changes as needed. Any changes made in your editor will reflect immediately in the application.

**Please do not use this in production. This is only for development.**

## Technical Details

- The development server runs on `localhost:8002`.
- The application operates within the Django request lifecycle. As a result, file uploads and embeddings may take some time to process.
- Streaming is not supported in this setup because it is not running under ASGI. The real deployment will handle these processes in the background to ensure optimal performance.


## Testing Dynamic Modules with ASGI

To test your dynamic module on an ASGI server for streaming and real-time responses, follow these steps:

1. **Note:** This real-time server does NOT capture automatic changes. You will need to restart the containers to apply any updates.

2. When you're ready to test async features in a more production-like environment, uncomment the following services in your `docker-compose.yml`:
```yaml
# Uncomment these services for async testing
# kitchenai-stream:
# kitchenai-qcluster:
# chromadb:
# postgres:
```

3. To restart the containers, you can run the following script outside your DevContainer:
```bash
./restart-stream.sh
```

This script will help you quickly restart the necessary services to test your changes in a real-time environment.

