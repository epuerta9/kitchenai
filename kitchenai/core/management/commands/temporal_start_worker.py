from django.core.management.base import BaseCommand
import asyncio
import concurrent.futures

class Command(BaseCommand):
    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument(
            '--module',
            dest='module_path',
            default=None,
            help='Specifies the kitchenai module to load'
        )

    def handle(self, *args, **options):
        """Runs the worker"""
        from temporalio.worker import Worker
        from kitchenai.core.temporal import get_temporal_client
        from kitchenai.core.workflows import KitchenAICoreWorkflow
        from kitchenai.core.activities import CoreManagerActivities
        async def run_worker():
            client = await get_temporal_client()
            manager = CoreManagerActivities(module="kitchenai.core.agents.CoreAgent")

            # Create the worker
            task_queue = "your-task-queue"
            with concurrent.futures.ThreadPoolExecutor(max_workers=100) as activity_executor:
                worker = Worker(
                    client,
                    task_queue=task_queue,
                    workflows=[KitchenAICoreWorkflow],
                    activities=[
                        manager.chat,
                    ],
                    activity_executor=activity_executor,
                )

                print(f"Starting worker, connecting to task queue: {task_queue}")
                await worker.run()

        # Run the worker
        asyncio.run(run_worker())