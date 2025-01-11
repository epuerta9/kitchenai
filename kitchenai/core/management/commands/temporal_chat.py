from django.conf import settings
import os
from django.core.management.base import BaseCommand



class Command(BaseCommand):
    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument(
            '--module',
            dest='module_path',
            default=None,
            help='Specifies the kitchenai module to load'
        )

    def run(self, *args, **options):
        """Runs the server"""
        from kitchenai.core.temporal import get_temporal_client

        import asyncio

        async def start_client():
            client = await get_temporal_client()
            self.stdout.write(self.style.SUCCESS("Connected to Temporal server"))
            return client

        # Run the async function in the event loop
        client = asyncio.run(start_client())