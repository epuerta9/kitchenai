from django.core.management.base import BaseCommand
from django.core.management import call_command
from kitchenai.core.models import KitchenAIManagement, KitchenAIModules
import logging 
import pathlib
import yaml

logger = logging.getLogger("kitchenai.core.commands")


class Command(BaseCommand):
    help = 'Inits kitchenai'

    def handle(self, *args, **options):
        """Checks to see if there is a kitchen.yml in the root directory, loads and initializes the db"""

        config = pathlib.Path.cwd() / "kitchenai.yml"
        config_data = self.read_yaml_config(config)

        if config_data:
            # Save the configuration to the database
            self.save_config_to_db(config_data)
            self.stdout.write(self.style.SUCCESS('KitchenAI initialized and configuration saved successfully.'))
        else:
            self.stdout.write(self.style.ERROR('Failed to read the config file.'))

        try:
            KitchenAIManagement.objects.create()
        except Exception as e:
            logger.info("management table has been initialized")
            pass

    def read_yaml_config(self, yaml_file_path):

        # Check if the file exists
        if not yaml_file_path.is_file():
            self.stdout.write(self.style.ERROR(f"YAML config file kitchenai.yml not found."))
            return None

        # Read the YAML file
        with open(yaml_file_path, 'r') as file:
            try:
                return yaml.safe_load(file)
            except yaml.YAMLError as e:
                self.stdout.write(self.style.ERROR(f"Error reading YAML file: {e}"))
                return None

    def save_config_to_db(self, config):
        # Clear existing config
        KitchenAIManagement.objects.all().delete()

        mgmt = KitchenAIManagement.objects.create()
        
        # Save the main app module
        try:
            app = config["app"]
            KitchenAIModules.objects.create(
                name=app,
                kitchen = mgmt
            )
        except KeyError:
            logger.error("error app key is missing in config")
            return 
        except Exception as e:
            logger.error(e)
            return 
        