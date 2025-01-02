from ninja import Router
from ninja import Schema
from django.http import HttpResponse
import logging
from django.apps import apps
from typing import List
from .api.query import router as query_router
from .api.agent import router as agent_router
from .api.embedding import router as embedding_router
from .api.file import router as file_router

logger = logging.getLogger(__name__)

router = Router()
router.add_router("/query", query_router, tags=["query"])
#router.add_router("/agent", agent_router, tags=["agent"])
router.add_router("/embeddings", embedding_router, tags=["embeddings"])
router.add_router("/file", file_router, tags=["file"]) 

@router.get("/health")
async def default(request):
    return {"msg": "ok"}


class KitchenAIAppSchema(Schema):
    namespace: str
    query_handlers: List[str]
    agent_handlers: List[str]
    embed_handlers: List[str]
    storage_handlers: List[str]
import logging
logger = logging.getLogger(__name__)    

@router.get("/labels", response=KitchenAIAppSchema)
async def labels(request):
    """Lists all the custom kitchenai labels"""
    core_app = apps.get_app_config("core")
    if not core_app.kitchenai_app:
        logger.error("No kitchenai app in core app config")
        return HttpResponse(status=404)
    return core_app.kitchenai_app.to_dict()


