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
# router.add_router("/query", query_router, tags=["deprecated"])
# #router.add_router("/agent", agent_router, tags=["agent"])
# router.add_router("/embeddings", embedding_router, tags=["deprecated"])
# router.add_router("/file", file_router, tags=["deprecated"]) 


class KitchenAIAppSchema(Schema):
    namespace: str
    query_handlers: List[str]
    agent_handlers: List[str]
    embed_handlers: List[str]
    storage_handlers: List[str]
import logging
logger = logging.getLogger(__name__)    


