import logging
from kitchenai_rag_simple_bento.kitchen import app as kitchen
from kitchenai_llama.storage.llama_parser import Parser
from kitchenai.contrib.kitchenai_sdk.schema import StorageSchema
from kitchenai_rag_simple_bento.kitchen import chroma_collection
import os


from llama_index.core.node_parser import TokenTextSplitter
from llama_index.core.extractors import (
    TitleExtractor,
    QuestionsAnsweredExtractor)
from llama_index.core import Document
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.vector_stores.chroma import ChromaVectorStore

logger = logging.getLogger(__name__)

@kitchen.storage.handler("kitchenai-bento-simple-rag")
def simple_storage(data: StorageSchema, **kwargs):
    parser = Parser(api_key=os.environ.get("LLAMA_CLOUD_API_KEY", None))
    response = parser.load(data.dir, metadata=data.metadata, **kwargs)
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    VectorStoreIndex.from_documents(
        response["documents"], storage_context=storage_context, show_progress=True,
            transformations=[TokenTextSplitter(), TitleExtractor(),QuestionsAnsweredExtractor()]
    )