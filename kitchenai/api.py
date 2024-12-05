import logging

from django.apps import apps
from kitchenai.core.api import router as core_router
from ninja import NinjaAPI

logger = logging.getLogger(__name__)

api = NinjaAPI(version="0.8.0")


# Ensure `ready()` is called for all apps
apps.get_app_configs()

# Get the app's router from `MyAppConfig` and add it to the main API
api.add_router("/core", core_router)  # Add app's router here
