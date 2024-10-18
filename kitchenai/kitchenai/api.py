from ninja import NinjaAPI
from django.conf import settings
from importlib import import_module
import logging
import os 
import sys 

logger = logging.getLogger(__name__)

api = NinjaAPI()

@api.get("/testing")
def some_test(request):
    return {"msg" : "ok"}


@api.get("/health")
def default(request):

    return {"msg":"ok"}


def dynamic_routes():
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

# dynamic_routes()