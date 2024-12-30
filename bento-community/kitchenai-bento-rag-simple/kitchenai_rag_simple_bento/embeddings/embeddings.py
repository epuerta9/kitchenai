from kitchenai_rag_simple_bento.kitchen import app as kitchen
from kitchenai.contrib.kitchenai_sdk.schema import EmbedSchema
import logging
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.core.node_parser import TokenTextSplitter
from llama_index.core.extractors import (
    TitleExtractor,
    QuestionsAnsweredExtractor)
from llama_index.core import Document
from django.apps import apps
logger = logging.getLogger(__name__)


@kitchen.embeddings.handler("kitchenai-bento-simple-rag")
def simple_rag_bento_vagh(data: EmbedSchema):
    documents = [Document(text=data.text)]
    vector_store = apps.get_app_config("kitchenai_rag_simple_bento").vector_store
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    VectorStoreIndex.from_documents(
        documents, storage_context=storage_context, show_progress=True,
            transformations=[TokenTextSplitter(), TitleExtractor(),QuestionsAnsweredExtractor()]
    )





