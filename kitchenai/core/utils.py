import logging
import os
import sys
from importlib import import_module
from typing import TYPE_CHECKING

import yaml
from django.conf import settings
from kitchenai.contrib.kitchenai_sdk.kitchenai import KitchenAIApp
from kitchenai.core.models import KitchenAIManagement

if TYPE_CHECKING:
    from ninja import NinjaAPI

logger = logging.getLogger("kitchenai.core.utils")

def load_config_from_db(config: dict):
    try:
        mgmt = KitchenAIManagement.objects.get(name="kitchenai_management")
    except KitchenAIManagement.DoesNotExist:
        return config
    
    try:
        app = mgmt.kitchenaimodules_set.filter(is_root=True).first()
        if app:
            config["app"] = yaml.safe_load(app.name)
    except KitchenAIManagement.DoesNotExist:
        pass
    return config

def update_installed_apps(self, apps):
    if apps:
        settings.INSTALLED_APPS += tuple(apps)
        self.stdout.write(self.style.SUCCESS(f'Updated INSTALLED_APPS: {settings.INSTALLED_APPS}'))

def import_modules(module_paths):
    for name, path in module_paths.items():
        try:
            module_path, instance_name = path.split(':')
            module = import_module(module_path)
            instance = getattr(module, instance_name)
            globals()[name] = instance
            logger.info(f'Imported {instance_name} from {module_path}')
        except (ImportError, AttributeError) as e:
            logger.error(f"Error loading module '{path}': {e}")

def import_cookbook(module_path):
    try:
        module_path, instance_name = module_path.split(':')
        module = import_module(module_path)
        instance = getattr(module, instance_name)
        print(f'Imported {instance_name} from {module_path}')
        return instance
    except (ImportError, AttributeError) as e:
        print(f"Error loading module '{e}")



def setup(api: "NinjaAPI", module: str = ""):
    # # Load configuration from the database
    config = {}
    config = load_config_from_db(config)
    # Determine the user's project root directory (assumes the command is run from the user's project root)
    project_root = os.getcwd()

    # Add the user's project root directory to the Python path
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    if not config:
        logger.error('No configuration found. Checking dynamic module load')
        if module:
            logger.debug(f"importing module: {module}")
            config["app"] = module
        else:
            logger.error("error not configured correctly. No module found in command or config")
            return

    # Update INSTALLED_APPS and import modules
    # self.update_installed_apps(config.get('installed_apps', []))

    # self.import_modules(config.get('module_paths', {}))


    #importing main app
    try:
        module_path, instance_name = config["app"].split(':')
        module = import_module(module_path)
        instance = getattr(module, instance_name)

        logger.info(f'Imported {instance_name} from {module_path}')
        if isinstance(instance, KitchenAIApp):
            logger.info(f'{instance_name} is a valid KitchenAIApp instance.')
            api.add_router(f"/{instance._namespace}", instance._router)
        else:
            logger.error(f'{instance_name} is not a valid KitchenAIApp instance.')

    except (ImportError, AttributeError) as e:
        logger.error(f"Error loading module: {e}")
