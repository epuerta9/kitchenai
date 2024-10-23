from ninja import Router, Schema,File
from kitchenai.contrib.kitchenai_sdk.kitchenai import KitchenAIApp
from ninja.files import UploadedFile

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext
from llama_index.vector_stores.chroma import ChromaVectorStore

from llama_index.llms.openai import OpenAI
import os 
import tempfile
import chromadb
from typing import Optional
from llama_index.llms.openai import OpenAI



router = Router()

# create client and a new collection
chroma_client = chromadb.EphemeralClient()
chroma_collection = chroma_client.create_collection("quickstart")
llm = OpenAI(model="gpt-4")


class Query(Schema):
    query: str

kitchen = KitchenAIApp(router=router)


@kitchen.storage("storage")
def chromadb_storage(request, file: UploadedFile = File(...)):
    """
    Store uploaded files into a vector store
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        # Define the path for the temporary file
        temp_file_path = os.path.join(temp_dir, file.name)
        
        # Save the uploaded file as a temporary file
        with open(temp_file_path, "wb") as temp_file: 
            for chunk in file.chunks():
                temp_file.write(chunk)

        # Load data using SimpleDirectoryReader pointing to the temporary directory
        documents = SimpleDirectoryReader(input_dir=temp_dir).load_data()

    # set up ChromaVectorStore and load in data
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    VectorStoreIndex.from_documents(
        documents, storage_context=storage_context
    )
    return {"msg": "ok"}


@kitchen.query("query")
async def query(request, query: Query):
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

    index = VectorStoreIndex.from_vector_store(
        vector_store,
    )

    chat_engine = index.as_chat_engine(chat_mode="best", llm=llm, verbose=True)
    response = await chat_engine.achat(query.query)

    return {"msg": response.response}