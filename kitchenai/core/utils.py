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
from django.conf import settings
if TYPE_CHECKING:
    from ninja import NinjaAPI
from django_q.tasks import async_task

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



def setup(api: "NinjaAPI", module: str = "", project_root: str = os.getcwd()) -> "KitchenAIApp":
    # # Load configuration from the database
    # Determine the user's project root directory (assumes the command is run from the user's project root)
    # Add the user's project root directory to the Python path
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    if module:
        logger.debug(f"importing module: {module}")
        add_module_to_core(module)

    else:
        logger.info("No module found in command or config. Running without any dynamic modules")
        return



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

        print(f"module_path in add_module_to_core: {module_path}, instance name: {instance_name}")
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

    except ValueError as e:
        logger.error(f"Invalid module path format. Expected 'module:instance' {e}")

    except Exception as e:
        logger.error(f"error adding module to core: {e}")

def add_package_to_core(package_name: str):
    """
    Add a package to the core app. Only one bento box can be added to the core app at a time.
    """
    try:
        package = import_module(package_name)
        instance = getattr(package, "app")
        logger.info(f"Imported app from {package_name}") 
        if isinstance(instance, KitchenAIApp):
            #add the instance to the core app
            core_app = apps.get_app_config("core")
            core_app.kitchenai_app = instance
            logger.info(f'{package_name} is a valid KitchenAIApp instance.')
        else:
            logger.error(f'{package_name} is not a valid KitchenAIApp instance.')
        return instance
    except (ImportError, AttributeError) as e:
        logger.error(f"Error loading module '{e}")

#TODO: remove the kitchenai mgmt db work. Most of the time we are just adding a bento box to the core app. without the need to manage state 
#especially since kitchenai environments are so dynamic. It makes more sense to keep it at config runtime level.

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
    """
    Set the core kitchenai_app whether its bento or dynamic module.
    """
    mgmt = KitchenAIManagement.objects.get(name="kitchenai_management")
    if mgmt.module_path == "bento":
            add_bento_box_to_core()
    else:
        logger.info(f"Adding module to core: {mgmt.module_path}")
        project_root = os.getcwd()
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        add_module_to_core(mgmt.module_path)


    core_app = apps.get_app_config("core")
    if core_app.kitchenai_app:
        return core_app.kitchenai_app
    else:
        logger.error("No kitchenai app in core app config")
        raise Exception("No kitchenai app in core app config")


def add_bento_box_to_core():
    from kitchenai.bento.models import Bento
    bento_box = Bento.objects.first()
    if bento_box:
        bento_box.add_to_core()
    else:
        logger.error("No bento box found")
        raise Exception("No bento box found")
    

def run_django_q_task(task_name: str, *args, **kwargs):
    if settings.KITCHENAI_LOCAL:
        # Split task name into module path and function name
        # e.g. 'deepeval_plugin.tasks.run_contextual_relevancy' ->
        # module_path='deepeval_plugin.tasks', function_name='run_contextual_relevancy'
        module_path, function_name = task_name.rsplit('.', 1)
        
        # Import the module dynamically
        module = __import__(module_path, fromlist=[function_name])
        
        # Get the function from the module
        task_func = getattr(module, function_name)
        
        # Execute the function directly with provided args
        result = task_func(*args, **kwargs)
        return result
    async_task(task_name, *args, **kwargs)