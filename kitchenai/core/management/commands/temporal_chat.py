from django.conf import settings
import os
from django.core.management.base import BaseCommand
import asyncio
from kitchenai.core.workflows import ChatSignal

async def start_chat_workflow(prompt, workflow_id):
    from kitchenai.core.temporal import get_temporal_client
    from kitchenai.core.workflows import ChatSignal, KitchenAICoreWorkflow

    temporal_client = await get_temporal_client()
    
    # Get handle to existing workflow
    handle = temporal_client.get_workflow_handle(workflow_id)
    
    # Send chat signal to the workflow
    await handle.signal(KitchenAICoreWorkflow.chat, ChatSignal(message=prompt))

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
        """Starts the chat workflow in a background task"""
        prompt = options['prompt']
        workflow_id = options['workflow_id']
        
        # Create new event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Schedule the coroutine and run it for a short duration
            task = loop.create_task(start_chat_workflow(prompt, workflow_id))
            # Run for just 1 second to allow the workflow to start
            loop.run_until_complete(asyncio.wait([task], timeout=1))
            # Detach the task to let it continue running
            task.add_done_callback(lambda t: None)
        finally:
            loop.close()

        self.stdout.write(self.style.SUCCESS(f"Chat sent to workflow {workflow_id}"))