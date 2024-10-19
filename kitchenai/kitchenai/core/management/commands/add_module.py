import logging

from django.core.management.base import BaseCommand
from kitchenai.core.models import KitchenAIManagement
from kitchenai.core.models import KitchenAIModules

logger = logging.getLogger("kitchenai.core.commands")

class Command(BaseCommand):
    help = 'Runs the development server with dynamic route registration'

    def add_arguments(self, parser):
        # Add a positional argument
        parser.add_argument('module', type=str, help='Load kitchenAI app module')


    def handle(self, *args, **options):
        module = options.get("module")


        try:
            mgmt = KitchenAIManagement.objects.get(name="kitchenai_management")
        except KitchenAIManagement.DoesNotExist:
            logging.exception("error kitchenai database has not been initialized.")
            logging.exception("try kitchenai init")
            return

        #Add the module to the module table
        try:
            module = KitchenAIModules.objects.create(name=module, kitchen=mgmt)
        except Exception:
            logging.exception("error module already loaded.")
            return

        logger.info(f"module loaded: {module}")
