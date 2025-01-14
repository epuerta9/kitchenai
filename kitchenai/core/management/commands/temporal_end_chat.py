from django.core.management.base import BaseCommand
import asyncio

async def end_chat_workflow(workflow_id):
    from kitchenai.core.temporal import get_temporal_client
    from kitchenai.core.workflows import KitchenAICoreWorkflow

    temporal_client = await get_temporal_client()

    # Send the cancel signal to the workflow
    handle = temporal_client.get_workflow_handle(workflow_id)
    await handle.signal(KitchenAICoreWorkflow.cancel)

class Command(BaseCommand):
    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument(
            '--workflow-id',
            dest='workflow_id',
            required=True,
            help='Specifies the workflow ID to end'
        )

    def handle(self, *args, **options):
        """Ends the chat workflow in a background task"""
        workflow_id = options['workflow_id']
        
        # Create new event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Schedule the coroutine and run it for a short duration
            task = loop.create_task(end_chat_workflow(workflow_id))
            # Run for just 1 second to allow the workflow to start
            loop.run_until_complete(asyncio.wait([task], timeout=1))
            # Detach the task to let it continue running
            task.add_done_callback(lambda t: None)
        finally:
            loop.close()

        self.stdout.write(self.style.SUCCESS(f"Chat workflow {workflow_id} ended in the background."))