from django.conf import settings
import os
from django.core.management.base import BaseCommand
import asyncio
import logging

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),  # Console output
            logging.FileHandler('temporal_activities.log')  # File output
        ]
    )



async def start_workflow(prompt, workflow_id):
    from kitchenai.core.temporal import get_temporal_client
    from kitchenai.core.workflows import KitchenAICoreWorkflow, CoreParams
    from kitchenai.core.activities import ChatMessage
    temporal_client = await get_temporal_client()
    task_queue = "your-task-queue"

    # Create a CoreParams instance
    params = CoreParams(message=prompt)

    # Start the workflow with the CoreParams instance
    work = await temporal_client.start_workflow(
        KitchenAICoreWorkflow.run,
        args=[params],  # Pass the CoreParams instance
        id=workflow_id,
        task_queue=task_queue,
    )
    await work.signal(KitchenAICoreWorkflow.chat, ChatMessage(message=prompt))

class Command(BaseCommand):
    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument(
            '--prompt',
            dest='prompt',
            required=True,
            help='Specifies the prompt to send to the workflow'
        )
        parser.add_argument(
            '--workflow-id',
            dest='workflow_id',
            required=True,
            help='Specifies a unique workflow ID'
        )

    def handle(self, *args, **options):
        """Starts the workflow in a background task"""
        setup_logging()
        prompt = options['prompt']
        workflow_id = options['workflow_id']
        
        # Create and set new event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            # Schedule the coroutine and run it for a short duration
            task = loop.create_task(start_workflow(prompt, workflow_id))
            # Run for just 1 second to allow the workflow to start
            loop.run_until_complete(asyncio.wait([task], timeout=1))
            # Detach the task to let it continue running
            task.add_done_callback(lambda t: None)
        finally:
            loop.close()

        self.stdout.write(self.style.SUCCESS("Workflow started in the background."))