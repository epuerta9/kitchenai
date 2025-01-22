import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kitchenai.settings")

django_asgi = get_asgi_application()

# Starlette serving
from starlette.applications import Starlette
from starlette.routing import Mount
from django.conf import settings

from contextlib import asynccontextmanager
from kitchenai.core.broker import whisk

@asynccontextmanager
async def broker_lifespan(app):
    await whisk.broker.start()
    try:
        yield
    finally:
        await whisk.broker.close()


app = Starlette(
    routes=(
        Mount("/", django_asgi),  # redirect all requests to Django
    ),
    lifespan=broker_lifespan
)
application = app
