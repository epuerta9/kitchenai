from django.core.management.base import BaseCommand
from django.core.management import call_command
from kitchenai.core.models import KitchenAIManagement, KitchenAIModules
import logging

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
            logging.error("error kitchenai database has not been initialized.")
            logging.error("try kitchenai init")
            return
        
        #Add the module to the module table 
        try:
            module = KitchenAIModules.objects.create(name=module, kitchen=mgmt)
        except Exception as e:
            logging.error("error module already loaded.")
            return

        logger.info(f"module loaded: {module}")

