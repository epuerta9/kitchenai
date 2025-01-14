from temporalio.client import Client
import importlib
from temporalio.worker import Worker
from kitchenai.core import activities
from kitchenai.core import workflows
import asyncio
import signal


async def get_temporal_client(endpoint: str = "localhost:7233"):
    return await Client.connect(endpoint)

def load_dynamic_component(component_path: str):
    """Dynamically import a component from a string path."""
    module_path, component_name = component_path.rsplit('.', 1)
    module = importlib.import_module(module_path)
    return getattr(module, component_name)


async def start_worker(
    workflow_paths: list[str] = None,
    activity_paths: list[str] = None,
    task_queue: str = "kitchenai-task-queue"
):
    client = await get_temporal_client()
    loop = asyncio.get_event_loop()

    worker = Worker(
            client,
            task_queue=task_queue,
            workflows=[workflows.KitchenAICoreWorkflow],
            activities=[activities.CoreManagerActivities.chat],
            activity_executor=loop,
        )
    
    async def shutdown_worker():
        await worker.shutdown()

    loop.add_signal_handler(signal.SIGTERM, lambda: asyncio.create_task(shutdown_worker()))

    await worker.run()

# Usage example:
"""
await start_worker(
    workflow_paths=[
        'kitchenai.core.workflows.EntityBedrockWorkflow',
        'kitchenai.core.workflows.AnotherWorkflow'
    ],
    activity_paths=[
        'kitchenai.core.activities.prompt_bedrock',
        'kitchenai.core.activities.another_activity'
    ]
)
"""