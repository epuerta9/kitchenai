import logging

from django.apps import apps
from ninja import NinjaAPI
from kitchenai.core.router import router as core_router
from django.conf import settings
from ninja.security import HttpBearer


class AuthBearer(HttpBearer):
    def authenticate(self, request, token):
        defined_tokens = settings.KITCHENAI_JWT_SECRET.split(",")
        for t in defined_tokens:
            if token == t:
                return token
        return None


logger = logging.getLogger(__name__)



api = NinjaAPI(version="0.11.0", auth=AuthBearer() if settings.KITCHENAI["settings"]["auth"] else None)


apps.get_app_configs()

api.add_router("/v1", core_router)  
