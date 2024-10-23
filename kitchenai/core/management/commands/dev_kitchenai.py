import logging
import os
import sys
from importlib import import_module

import django
import yaml
from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand
from kitchenai.api import api
from kitchenai.core.models import KitchenAIManagement

logger = logging.getLogger("kitchenai.core.commands")

class Command(BaseCommand):
    help = 'Runs the development server'


    def handle(self, *args, **options):
        django.setup()
        # Load configuration from the database
        config = self.load_config_from_db()

        if not config:
            self.stdout.write(self.style.ERROR('No configuration found. Please run "kitchenai init" first.'))
            return

        # Update INSTALLED_APPS and import modules
        # self.update_installed_apps(config.get('installed_apps', []))
        self.set_app(config.get("app"))
        # self.import_modules(config.get('module_paths', {}))
        if settings.KITCHENAI_APP:

            # Determine the user's project root directory (assumes the command is run from the user's project root)
            project_root = os.getcwd()

            # Add the user's project root directory to the Python path
            if project_root not in sys.path:
                sys.path.insert(0, project_root)

            print(f"in dynamic routes: {settings.KITCHENAI_APP}")
            module_path, instance_name = settings.KITCHENAI_APP.split(':')
            print(f"module path {module_path}")
            print(f"instance name: {instance_name}")
            try:
                module_path, instance_name = settings.KITCHENAI_APP.split(':')
                module = import_module(module_path)
                instance = getattr(module, instance_name)

                logger.info(f'Imported {instance_name} from {module_path}')
            except (ImportError, AttributeError) as e:
                logger.error(f"Error loading module: {e}")

            print(instance)
            api.add_router("/core", instance)
        call_command('runserver', *args, **options)


    def load_config_from_db(self):
        config = {}
        mgmt = KitchenAIManagement.objects.get(name="kitchenai_management")

        app = mgmt.kitchenaimodules_set.first()
        config["app"] = yaml.safe_load(app.name)
        return config

    def update_installed_apps(self, apps):
        if apps:
            settings.INSTALLED_APPS += tuple(apps)
            self.stdout.write(self.style.SUCCESS(f'Updated INSTALLED_APPS: {settings.INSTALLED_APPS}'))

    def set_app(self, app):
        if app:
            # Set the KITCHENAI_APP setting dynamically
            settings.KITCHENAI_APP = app
            self.stdout.write(self.style.SUCCESS(f'KITCHENAI_APP set to: {settings.KITCHENAI_APP}'))

    def import_modules(self, module_paths):
        for name, path in module_paths.items():
            try:
                module_path, instance_name = path.split(':')
                module = import_module(module_path)
                instance = getattr(module, instance_name)
                globals()[name] = instance
                self.stdout.write(self.style.SUCCESS(f'Imported {instance_name} from {module_path}'))
            except (ImportError, AttributeError) as e:
                self.stdout.write(self.style.ERROR(f"Error loading module '{path}': {e}"))
