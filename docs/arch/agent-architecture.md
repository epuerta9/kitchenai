Below is a **proposed framework** for integrating **Agents**, **Temporal**, and **LlamaIndex** workflows in **KitchenAI**. It brings together your ideas about:

1. A **`@app.handler.agent`** for LlamaIndex-based “thinking” (single- or multi-agent).  
2. Each handler mapping to a **Temporal Activity** inside a larger Temporal Workflow.  
3. A **project management agent** that monitors everything, providing a single interface for user interactions.  
4. A **Django** environment for orchestrating deployment, logging, DB usage, and more.  

I’ll walk through the architecture and provide **step-by-step** details on how you might implement this in **KitchenAI**.

---

# 1. High-Level Architecture

**KitchenAI + Django + Temporal**:

```
 ┌──────────────────────────┐       ┌───────────────────────────────┐
 │   Django (KitchenAI)     │       │   Temporal Server / Web UI    │
 │  - Exposes /api/v1/...   │       │  (Hosted outside Django)       │
 │  - Has bento boxes       │       └───────────────┬───────────────┘
 │  - Has mgmt commands     │                       │
 │  (Project Mgmt Agent)    │ (HTTP/gRPC to start)   │
 └──────────────┬───────────┘                       │
                │                                   │
        ┌───────▼─────────────────┐       ┌────────▼─────────────────────┐
        │  Container for Worker   │       │  Container for Worker (opt)  │
        │  - Django mgmt command  │       │   or same container          │
        │  - Runs Temporal worker │       └───────────────────────────────┘
        │  - Has agent code, etc. │
        └─────────────────────────┘
```

- **Django**:  
  - Where **KitchenAI** runs, exposing HTTP endpoints.  
  - Has all your “bento boxes,” including the “project management agent.”  
  - Defines **Temporal workflow stubs** and starts them.  
- **Temporal Workers**:  
  - Deployed as Django management commands (like `python manage.py run_temporal_worker`).  
  - Each worker loads the **activities** defined by your agent handlers (`@app.handler.agent`).  
  - These activities can do anything: call LlamaIndex, query the Django ORM, emit events via Redis, etc.

---

# 2. Defining an Agent Handler That Maps to a Temporal Activity

## 2.1 The `@app.handler.agent` Decorator

You described a `@app.handler.agent` that will be **LlamaIndex-based**. Something like:

```python
# my_bento/handlers.py
from kitchenai.core.app import handler

@handler.agent(name="my_llama_index_agent")
def llama_agent_think(prompt: str) -> str:
    """
    A simple agent function that uses LlamaIndex to think.
    Could be a single agent or a small chain of 'reasoning'.
    """
    from llama_index import GPTSimpleVectorIndex  # or similar
    # (Pseudo-code) Access your index
    index = GPTSimpleVectorIndex.load_from_disk("my_index.json")
    response = index.query(prompt)
    return str(response)
```

- This `llama_agent_think` function is the **core** “thinking step.”  
- Under the hood, we want to **turn it into a Temporal Activity** so that it can be invoked as part of a larger workflow.

## 2.2 Registering as a Temporal Activity

We’ll define a standard way for KitchenAI to **discover** any `@handler.agent` function and expose it as a **Temporal Activity**.

One approach:

```python
# my_bento/temporal_activities.py
from kitchenai.contrib.temporal import temporal_activity

@temporal_activity
def llama_agent_think(prompt: str) -> str:
    # Possibly re-use the same code from 'handlers.py'
    # or directly import the function from handlers.py

    from llama_index import GPTSimpleVectorIndex
    index = GPTSimpleVectorIndex.load_from_disk("my_index.json")
    response = index.query(prompt)
    return str(response)
```

But if we want to unify them, we can decorate with both:

```python
@handler.agent(name="my_llama_index_agent")
@temporal_activity
def llama_agent_think(prompt: str) -> str:
    ...
```

**Important**:  
- The `temporal_activity` decorator adds metadata so the **Temporal Worker** knows to load and register this function as an **Activity**.  
- The `@handler.agent` gives KitchenAI’s HTTP side a way to call it directly if needed.

---

# 3. Creating a Temporal Workflow

## 3.1 Example Workflow Definition

We can define a **Temporally** orchestrated workflow that calls multiple “Agent Activities”:

```python
# my_bento/workflows.py
from kitchenai.contrib.temporal import temporal_workflow
from my_bento.temporal_activities import llama_agent_think

@temporal_workflow
class MyCompositeWorkflow:
    """
    A workflow that orchestrates multiple agent activities
    to achieve an output.
    """
    @staticmethod
    async def run_workflow(input_data: dict) -> dict:
        """
        The main entrypoint for the workflow logic.
        Could call multiple activity fns,
        or just one if it's a simple use case.
        """
        # 1. Call the LlamaIndex agent activity
        result1 = await llama_agent_think(prompt="Hello, can you analyze X?")

        # 2. Possibly call other agent activity
        # result2 = await some_other_agent_activity(...)

        # Combine or finalize
        final_result = {
            "agent_think": result1,
            # "other": result2
        }
        return final_result
```

### Key Points

- `temporal_workflow` is a decorator that ties into **KitchenAI** or a custom integration.  
- We define a `run_workflow` async method that calls our **activities** (like `llama_agent_think`) using Temporal’s standard async stub approach.  
- In real usage, you’d define stubs or rely on a codegen approach that references the `llama_agent_think` activity.

## 3.2 Starting the Workflow from Django

Inside your **Django** app, you might have:

```python
# my_bento/views.py
from django.http import JsonResponse
from kitchenai.contrib.temporal.client import get_workflow_client
from my_bento.workflows import MyCompositeWorkflow

def start_workflow_view(request):
    # 1. Parse input
    # 2. Start the workflow
    client = get_workflow_client()
    workflow_handle = client.start_workflow(MyCompositeWorkflow.run_workflow, input_data={})
    
    return JsonResponse({"workflow_id": workflow_handle.id, "status": "started"})
```

**Now**: The user or your “Project Management Agent” calls this endpoint to launch the workflow. 

---

# 4. Django Management Command to Run Temporal Worker

You mentioned wanting to **launch** the Temporal worker using a **Django management command**. Let’s call it `run_temporal_worker`.

```python
# my_bento/management/commands/run_temporal_worker.py
from django.core.management.base import BaseCommand
from kitchenai.contrib.temporal import start_temporal_worker

class Command(BaseCommand):
    help = "Run Temporal Worker for KitchenAI"

    def handle(self, *args, **options):
        # This method loads all 'temporal_activity' definitions
        # in the bento, then registers them with the worker
        start_temporal_worker()
```

**What `start_temporal_worker()` might do**:

1. **Import** all modules that define `@temporal_activity`.  
2. **Register** them with the Temporal Worker.  
3. **Block** and run the worker event loop.

Then you can run:

```bash
docker run -it my_bento_image python manage.py run_temporal_worker
```

**in a separate container** or as a separate process, ensuring it has access to **Django settings** (ORM, Redis, etc.).

---

# 5. Simple vs. Complex Cases

1. **Simple**: One workflow → One activity → One agent.  
   - In that scenario, your `MyCompositeWorkflow.run_workflow` basically just calls `llama_agent_think(prompt="...")` and returns.  

2. **Complex**: Many steps → Many activities → Possibly multiple agent handlers.  
   - The workflow can orchestrate them in sequence or parallel, storing partial results in the workflow state.

---

# 6. The “Project Management Agent”

You want a “Project Management Agent” that:

1. **Knows** about the Temporal workflow’s status.  
2. Serves as the **main user interface**.  
3. Can **ask** other specialized agents for sub-tasks or status.

## 6.1 Defining the Project Management Agent

```python
# project_management_agent.py
from kitchenai.core.app import handler
from kitchenai.contrib.temporal.client import get_workflow_client

@handler.agent(name="project_management_agent")
def project_management_interface(action: str, workflow_id: str=None, data: dict=None) -> dict:
    """
    The primary user-facing agent. 
    - 'action' might be 'start_workflow', 'get_status', 'cancel', etc.
    - 'workflow_id' references a specific Temporal workflow instance.
    - 'data' is any additional context or parameters.
    """

    client = get_workflow_client()

    if action == "start_workflow":
        # Start a new composite workflow
        handle = client.start_workflow(MyCompositeWorkflow.run_workflow, data or {})
        return {"workflow_id": handle.id, "status": "started"}

    elif action == "get_status" and workflow_id:
        # Query the workflow state
        # e.g. handle = client.get_workflow_handle(MyCompositeWorkflow.run_workflow, workflow_id)
        # state = handle.query(...) or handle.describe()
        # For demo:
        return {"workflow_id": workflow_id, "status": "ongoing"}

    elif action == "ask_subagent":
        # Possibly talk to another agent or run another activity
        # ...
        return {"message": "asking sub agent..."}

    # etc.
    return {"error": "Unknown action"}
```

**How It Works**:

- The user calls an endpoint in Django that triggers this agent’s function.  
- The agent can then start or query the **Temporal workflow**, or direct calls to other agent activities.  
- Because it’s all in Django, it has access to the **ORM** or any other system resources.

---

# 7. LlamaIndex Integration Details

1. **Storing Indices**:  
   - You might keep your LlamaIndex data (`.json` or `.index` files) in a known location (like `/app/kitchenai/dynamic/indices/`).  
2. **Loading**:  
   - Each activity function that uses LlamaIndex loads the appropriate index. Possibly use caching or a DB-stored approach to avoid reloading from disk each time.  
3. **Separate Indices per Agent**:  
   - If your “SalesAgent” uses one knowledge base, while “ProjectManagementAgent” references a different one, store them separately.

---

# 8. Putting It All Together: Example Lifecycle

### **Step 1**: Developer writes **agent handlers** + **temporal activities**.

```python
@handler.agent(name="sales_agent")
@temporal_activity
def sales_pipeline(prompt: str) -> str:
    # LlamaIndex or other logic
    ...

@handler.agent(name="marketing_agent")
@temporal_activity
def marketing_pipeline(prompt: str) -> str:
    ...
```

### **Step 2**: Developer writes a **Temporal Workflow** orchestrating them.

```python
@temporal_workflow
class MultiStepWorkflow:
    @staticmethod
    async def run_workflow(input_data: dict) -> dict:
        sales_resp = await sales_pipeline("Analyze sales data..")
        marketing_resp = await marketing_pipeline("Analyze marketing angles..")
        return {"sales": sales_resp, "marketing": marketing_resp}
```

### **Step 3**: “ProjectManagementAgent” is the **entry point** for user requests.

```python
@handler.agent(name="project_management_agent")
def pm_agent(action: str, data: dict=None):
    if action == "start_multistep":
        handle = client.start_workflow(MultiStepWorkflow.run_workflow, data or {})
        return {"workflow_id": handle.id, "message": "Workflow started!"}
    ...
```

### **Step 4**: Django management command `run_temporal_worker` loads all activities.

### **Step 5**: When a user calls `/api/v1/project_management_agent/` with `{"action": "start_multistep", ...}`, we:

1. **Parse** the request in Django.  
2. **Invoke** `pm_agent("start_multistep", data={...})`.  
3. The agent calls `client.start_workflow(...)`.  
4. **Temporal** runs the `MultiStepWorkflow`, which calls the `sales_pipeline` and `marketing_pipeline` activities.  
5. Results are stored in the workflow, eventually returning final output.

---

# 9. Advanced Considerations

1. **Async Django + Async Activities**:  
   - Make sure your Django container supports **async** if needed.  
   - The Temporal Python SDK can use `asyncio`-based workers.
2. **Scaling**:  
   - Each container running `run_temporal_worker` can scale horizontally to handle more activity calls.  
3. **Logging**:  
   - Activities can log to Django’s DB or a separate logging pipeline.  
4. **Human-in-the-Loop**:  
   - The workflow can **pause** waiting for user input. The “Project Management Agent” can signal the workflow with new data.  

---

# 10. Summary of the Framework

1. **Agent Handler Decorator** (`@app.handler.agent`):  
   - Mark any function as an agent entry point (e.g. “LlamaIndex-based logic”).  

2. **Temporal Activity Decorator** (`@temporal_activity`):  
   - Tells KitchenAI to register this agent function as a Temporal Activity.  

3. **Temporal Workflow**:  
   - Organized set of steps calling these agent activities.  
   - Possibly automatically generated or user-defined in code.  
   - Launched from Django via a client.  

4. **Project Management Agent**:  
   - A top-level agent that orchestrates user requests, starts workflows, queries status, or calls sub-agents.  
   - Exposed through your **bento box** as the main interface.  

5. **Django Management Command** (`run_temporal_worker`):  
   - Loads all activities and starts the Temporal worker.  
   - Runs in a separate container or process that has Django context.  

6. **Simple → Complex**:  
   - For small tasks, 1 workflow with 1 activity is enough.  
   - For bigger tasks, a multi-step workflow calls multiple agent activities.  

7. **Under the Hood**:  
   - The Bento box defines “which agent handlers exist.”  
   - The framework scans for these, registers them as activities, and either merges them into a **default** or a **user-defined** workflow.  
   - The entire pipeline is orchestrated by **Temporal** at runtime, with the “Project Management Agent” as your user-facing handle.

---

## Final Thoughts

Using this architectural approach, you achieve:

1. **Decoupled** Agent logic (LlamaIndex code) from the **Temporal workflow** orchestration.  
2. A **Django-based** bento environment for easy **deployment**, **management commands**, and **database** usage.  
3. A **Project Management Agent** as a single, user-friendly interface to see what’s happening across multiple agent workflows.  
4. **Scalability**: Because each agent activity can run in separate containers/workers, you can grow the system as needed.  

This framework ensures your KitchenAI-based “Agent + Temporal + LlamaIndex” solution remains both **modular** (agents as discrete activities) and **powerful** (chained via Temporal workflows), while **leveraging** Django for all the niceties—ORM, logging, admin commands, etc.