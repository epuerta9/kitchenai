import logging

from django.apps import apps
from ninja import NinjaAPI
from kitchenai.core.router import router as core_router
from kitchenai.core.api.openai import router as openai_router
from django.conf import settings
from ninja.security import HttpBearer
from kitchenai.exceptions import NoRespondersError  # Import from root exceptions


class AuthBearer(HttpBearer):
    def authenticate(self, request, token):
        defined_tokens = settings.KITCHENAI_JWT_SECRET.split(",")
        for t in defined_tokens:
            if token == t:
                return token
        return None


logger = logging.getLogger(__name__)



api = NinjaAPI(urls_namespace="v1", version="0.11.0", auth=AuthBearer() if settings.KITCHENAI["settings"]["auth"] else None)


apps.get_app_configs()

api.add_router("/api/ktch", core_router)  
api.add_router("", openai_router)

@api.exception_handler(NoRespondersError)
def handle_no_responders(request, exc):
    logger.error(f"No responders available for request: {exc}")
    return api.create_response(
        request,
        str(exc),
        status=503,
    )