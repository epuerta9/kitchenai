from llama_index_starter_bento.kitchen import app as kitchen
from kitchenai.contrib.kitchenai_sdk.schema import EmbedSchema
import logging

logger = logging.getLogger(__name__)


@kitchen.embed("kitchenai-bento-llama-index-starter")
async def embeddings(text: EmbedSchema, metadata: dict = {}, **kwargs):
    pass




