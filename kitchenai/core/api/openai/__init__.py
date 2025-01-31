from ninja import Router
from ninja import Schema
from django.http import HttpResponse
import logging
from django.apps import apps
from typing import List
from .files import router as files_router

logger = logging.getLogger(__name__)
from .chat import router as chat_router
from .embeddings import router as embeddings_router

router = Router()

router.add_router("/chat", chat_router, tags=["chat"])
router.add_router("/files", files_router, tags=["files"])

#TODO: embeddings endpoint not ready
#router.add_router("/embeddings", embeddings_router, tags=["embeddings"])


@router.get("/health")
async def default(request):
    return {"msg": "ok"}