import logging

from django.apps import apps
from ninja import NinjaAPI
from kitchenai.core.router import router as core_router

logger = logging.getLogger(__name__)

api = NinjaAPI(version="0.10.0")


apps.get_app_configs()

api.add_router("/v1", core_router)  
