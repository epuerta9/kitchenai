import logging

from django.apps import apps
from kitchenai.core.api import router as core_router
from ninja import NinjaAPI

logger = logging.getLogger(__name__)

api = NinjaAPI()


# Ensure `ready()` is called for all apps
apps.get_app_configs()

# Get the app's router from `MyAppConfig` and add it to the main API
api.add_router("/core", core_router)  # Add app's router here
try:
    kitchenai_config = apps.get_app_config("kitchenai_cookbook")
    kitchenai_config.kitchenai_app.register_api()
    api.add_router(kitchenai_config.kitchenai_app._namespace, kitchenai_config.kitchenai_app._router)  # Add app's router here
except:
    pass
