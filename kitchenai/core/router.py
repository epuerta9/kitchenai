from ninja import Router
from ninja import Schema
import logging
from typing import List


logger = logging.getLogger(__name__)

router = Router()


class KitchenAIAppSchema(Schema):
    namespace: str
    query_handlers: List[str]
    agent_handlers: List[str]
    embed_handlers: List[str]
    storage_handlers: List[str]
    
import logging
logger = logging.getLogger(__name__)    


