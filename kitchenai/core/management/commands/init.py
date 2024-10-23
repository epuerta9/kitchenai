import logging
import pathlib

import yaml
from django.core.management.base import BaseCommand
from kitchenai.core.models import KitchenAIDependencies
from kitchenai.core.models import KitchenAIManagement
from kitchenai.core.models import KitchenAIModules
from kitchenai.core.models import KitchenAIPlugins

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
            self.stdout.write(self.style.ERROR('No config file for kitchenai.'))

    def read_yaml_config(self, yaml_file_path):

        # Check if the file exists
        if not yaml_file_path.is_file():
            self.stdout.write(self.style.ERROR("YAML config file kitchenai.yml not found."))
            return None

        # Read the YAML file
        with open(yaml_file_path) as file:
            try:
                return yaml.safe_load(file)
            except yaml.YAMLError as e:
                self.stdout.write(self.style.ERROR(f"Error reading YAML file: {e}"))
                return None

    def save_config_to_db(self, config):
        # Clear existing config
        KitchenAIManagement.objects.all().delete()
        try:
            mgmt = KitchenAIManagement.objects.create(
                version = config["version"],
                project_name = config["project_name"]
            )
        except Exception as e:
            logger.error(e)
            return

        # Save the main app module
        try:
            app = config["app"]
            KitchenAIModules.objects.create(
                name=app,
                kitchen = mgmt,
                is_root = True
            )
            self.stdout.write(self.style.SUCCESS(f"main app loaded: {app}"))

        except KeyError as e:
            logger.error(e)
            return
        except Exception as e:
            logger.error(e)
            return

        #installed apps i.e cookbooks
        try:
            installed_apps = config["installed_apps"]
            for app in installed_apps:
                KitchenAIModules.objects.create(
                    name=app,
                    kitchen = mgmt,
                )
        except KeyError as e:
            logger.error(e)
            return
        except Exception as e:
            logger.error(e)
            return

        try:
            plugins = config.get("plugins", None)
            if plugins:
                for plugin in plugins:
                    KitchenAIPlugins.objects.create(
                        name=plugin,
                        kitchen = mgmt,
                    )
        except KeyError as e:
            logger.error(e)
            return
        except Exception as e:
            logger.error(e)
            return

        try:
            dependencies = config.get("dependencies", None)
            if dependencies:
                for dep in dependencies:
                    KitchenAIDependencies.objects.create(
                        name=dep,
                        kitchen = mgmt,
                    )
        except KeyError as e:
            logger.error(e)
            return
        except Exception as e:
            logger.error(e)
            return
