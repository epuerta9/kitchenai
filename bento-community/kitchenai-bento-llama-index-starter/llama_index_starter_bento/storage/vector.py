import logging
from llama_index_starter_bento.kitchen import app as kitchen

logger = logging.getLogger(__name__)



@kitchen.storage("kitchenai-bento-llama-index-starter")
def file_storage(dir: str, metadata: dict = {}, *args, **kwargs):
    """
    Example: 
        @kitchen.storage("file")
        def chromadb_storage(dir: str, metadata: dict = {}, *args, **kwargs):
            Store uploaded files into a vector store with metadata
            chroma_collection = chroma_client.get_or_create_collection("quickstart")
            parser = Parser(api_key=os.environ.get("LLAMA_CLOUD_API_KEY", None))
process
            response = parser.load(dir, metadata=metadata, **kwargs)

            vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

            # set up ChromaVectorStore and load in data
            storage_context = StorageContext.from_defaults(vector_store=vector_store)
                    
            # quickstart index
            VectorStoreIndex.from_documents(
                response["documents"], storage_context=storage_context, show_progress=True,
                    transformations=[TokenTextSplitter(), TitleExtractor(),QuestionsAnsweredExtractor()]
            )
            
            return {"msg": "ok", "documents": len(response["documents"])}
    
    """   

    
    return {"msg": "ok", "documents": "response"}
