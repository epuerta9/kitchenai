from kitchenai.core.models import KitchenAIManagement
from django.conf import settings
import yaml
from importlib import import_module
import logging

logger = logging.getLogger("kitchenai.core.utils")

def load_config_from_db():
    config = {}
    mgmt = KitchenAIManagement.objects.get(name="kitchenai_management")
    
    app = mgmt.kitchenaimodules_set.first()
    config["app"] = yaml.safe_load(app.name)
    return config

def update_installed_apps(self, apps):
    if apps:
        settings.INSTALLED_APPS += tuple(apps)
        self.stdout.write(self.style.SUCCESS(f'Updated INSTALLED_APPS: {settings.INSTALLED_APPS}'))

def set_app(app):
    if app:
        # Set the KITCHENAI_APP setting dynamically
        settings.KITCHENAI_APP = app
        logger.info(f'KITCHENAI_APP set to: {settings.KITCHENAI_APP}')

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