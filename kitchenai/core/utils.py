import logging
import os
import sys
from importlib import import_module
from typing import TYPE_CHECKING

from django.apps import apps
from django.conf import settings
from kitchenai.contrib.kitchenai_sdk.kitchenai import KitchenAIApp
from kitchenai.core.models import KitchenAIManagement
from kitchenai.core.models import KitchenAIRootModule

if TYPE_CHECKING:
    from ninja import NinjaAPI

logger = logging.getLogger("kitchenai.core.utils")


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



def setup(api: "NinjaAPI", module: str = "") -> "KitchenAIApp":
    # # Load configuration from the database
    config = {}
    # Determine the user's project root directory (assumes the command is run from the user's project root)
    project_root = os.getcwd()

    # Add the user's project root directory to the Python path
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    if module:
        logger.debug(f"importing module: {module}")
        config["app"] = module

        #add module to db
        root_module = get_or_create_root_module(config["app"])
        if root_module:
            root_module.name = config["app"]
            root_module.save()
    else:
        logger.info("No module found in command or config. Running without any dynamic modules")
        return

    add_module_to_core(config["app"])
    add_module_router(api)


def add_module_router(api: "NinjaAPI"):
    """
    Add a router to the api
    """
    core_app = apps.get_app_config("core")
    if core_app.kitchenai_app:
        core_app.kitchenai_app.register_api()
        api.add_router(f"/{core_app.kitchenai_app._namespace}", core_app.kitchenai_app._router)
    else:
        logger.error("No kitchenai app in core app config")
        return

def add_module_to_core(module_path: str):
    """
    Add a module to the core app
    """
    #importing main app
    try:
        module_path, instance_name = module_path.split(':')
        print(f"module_path in add_module_to_core: {module_path}")
        module = import_module(module_path)
        instance = getattr(module, instance_name)

        logger.info(f'Imported {instance_name} from {module_path}')
        if isinstance(instance, KitchenAIApp):
            #add the instance to the core app
            core_app = apps.get_app_config("core")
            core_app.kitchenai_app = instance
            logger.info(f'{instance_name} is a valid KitchenAIApp instance.')
        else:
            logger.error(f'{instance_name} is not a valid KitchenAIApp instance.')
        return instance

    except (ImportError, AttributeError) as e:
        logger.warning(f"No valid KitchenAIApp instance found: {e}")

def get_or_create_root_module(module_path: str):
    try:
        return KitchenAIRootModule.objects.get(name=module_path)
    except KitchenAIRootModule.DoesNotExist:
        kitchen_mgmt = KitchenAIManagement.objects.get(name="kitchenai_management")
        #create a new root module
        root_module = KitchenAIRootModule(name=module_path, kitchen=kitchen_mgmt)
        root_module.save()
        logger.warning(f"No root module found for {module_path}. Created new root module.")

def get_first_root_module() -> str:
    try:
        return KitchenAIRootModule.objects.first().name
    except KitchenAIRootModule.DoesNotExist:
        raise Exception("No root module found. Please create a root module first.")


def get_core_kitchenai_app():
    project_root = os.getcwd()

    # Add the user's project root directory to the Python path
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    root_module = get_first_root_module()

    print(f"root_module: {root_module}")
    add_module_to_core(root_module)
    core_app = apps.get_app_config("core")
    if core_app.kitchenai_app:
        return core_app.kitchenai_app
    else:
        logger.error("No kitchenai app in core app config")
        raise Exception("No kitchenai app in core app config")
