from kitchenai_rag_simple_bento.kitchen import app as kitchen
from kitchenai.contrib.kitchenai_sdk.schema import EmbedSchema
import logging
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core.node_parser import TokenTextSplitter
from llama_index.core.extractors import (
    TitleExtractor,
    QuestionsAnsweredExtractor)
from llama_index.core import Document
from kitchenai_rag_simple_bento.kitchen import chroma_collection

logger = logging.getLogger(__name__)


@kitchen.embeddings.handler("kitchenai-bento-simple-rag")
def simple_rag_bento_vagh(data: EmbedSchema):
    documents = [Document(text=data.text)]
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    VectorStoreIndex.from_documents(
        documents, storage_context=storage_context, show_progress=True,
            transformations=[TokenTextSplitter(), TitleExtractor(),QuestionsAnsweredExtractor()]
    )





