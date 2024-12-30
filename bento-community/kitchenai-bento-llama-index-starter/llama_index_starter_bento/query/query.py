from llama_index_starter_bento.kitchen import app as kitchen
from kitchenai.contrib.kitchenai_sdk.schema import QuerySchema
import logging

from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index_starter_bento.kitchen import chroma_collection, llm

logger = logging.getLogger(__name__)


@kitchen.query("kitchenai-bento-llama-index-starter")
async def query(data: QuerySchema):
    """
    Example: 
     @kitchen.query("query")
    async def query(data: QuerySchema):
        chroma_collection = chroma_client.get_or_create_collection("quickstart")


        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

        index = VectorStoreIndex.from_vector_store(
            vector_store,
        )

        query_engine = index.as_query_engine(chat_mode="best", llm=llm, verbose=True)
        response = await query_engine.aquery(data.query)

        return {"msg": response.response}
    """
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    index = VectorStoreIndex.from_vector_store(
        vector_store,
    )
    query_engine = index.as_query_engine(chat_mode="best", llm=llm, verbose=True)
    response = query_engine.query(data.query)

    return {"msg": response.response}




