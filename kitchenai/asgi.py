import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kitchenai.settings")

django_asgi = get_asgi_application()

# Starlette serving
from starlette.applications import Starlette
from starlette.routing import Mount

from contextlib import asynccontextmanager
# from .broker import broker


# @asynccontextmanager
# async def broker_lifespan(app):
#     await broker.start()
#     try:
#         yield
#     finally:
#         await broker.close()


app = Starlette(
    routes=(
        Mount("/", django_asgi),  # redirect all requests to Django
    ),
    # lifespan=broker_lifespan
)
application = app
