# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "kitchenai-whisk",
#   "kitchenai-llama",
#   "llama-index",
#   "llama-index-vector-stores-chroma",
#   "chromadb",
#   "tiktoken"
# ]
# ///

from whisk.kitchenai_sdk.kitchenai import KitchenAIApp
from whisk.kitchenai_sdk.schema import (
    WhiskQuerySchema,
    WhiskQueryBaseResponseSchema,
    WhiskStorageSchema,
    WhiskStorageResponseSchema,
    WhiskEmbedSchema,
    WhiskEmbedResponseSchema,
    TokenCountSchema
)

from llama_index.core import VectorStoreIndex, StorageContext, Document
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core.node_parser import TokenTextSplitter
from llama_index.core.extractors import TitleExtractor, QuestionsAnsweredExtractor
from llama_index.llms.openai import OpenAI
from llama_index.core.callbacks import CallbackManager, TokenCountingHandler
from llama_index.core import Settings
import chromadb
import logging
import asyncio
import tiktoken
from whisk.client import WhiskClient
from kitchenai_llama.storage.llama_parser import Parser
import os
import tempfile
from pathlib import Path

# Setup logging
logger = logging.getLogger(__name__)

# Initialize token counter
token_counter = TokenCountingHandler(
    tokenizer=tiktoken.encoding_for_model("gpt-3.5-turbo").encode
)
Settings.callback_manager = CallbackManager([token_counter])

# Initialize LLM
llm = OpenAI(model="gpt-3.5-turbo")
Settings.llm = llm

# Initialize Vector Store
chroma_client = chromadb.PersistentClient(path="chroma_db")
chroma_collection = chroma_client.get_or_create_collection("quickstart")
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

# Initialize KitchenAI App
kitchen = KitchenAIApp(namespace="llama-index")

@kitchen.query.handler("query")
async def query_handler(data: WhiskQuerySchema) -> WhiskQueryBaseResponseSchema:
    """Query handler with RAG"""
    # Create filters from metadata if provided
    filters = None
    if data.metadata:
        from llama_index.core.vector_stores.types import MetadataFilter, MetadataFilters
        print(data.metadata)
        filter_list = [
            MetadataFilter(key=key, value=value)
            for key, value in data.metadata.items()
        ]
        filters = MetadataFilters(filters=filter_list)

    # Create index and query engine
    index = VectorStoreIndex.from_vector_store(vector_store)
    query_engine = index.as_query_engine(
        chat_mode="best",
        filters=filters,
        llm=llm,
        verbose=True
    )

    # Execute query
    response = await query_engine.aquery(data.query)

    # Get token counts
    token_counts = {
        "embedding_tokens": token_counter.total_embedding_token_count,
        "llm_prompt_tokens": token_counter.prompt_llm_token_count,
        "llm_completion_tokens": token_counter.completion_llm_token_count,
        "total_llm_tokens": token_counter.total_llm_token_count
    }
    token_counter.reset_counts()

    return WhiskQueryBaseResponseSchema.from_llama_response(
        data,
        response,
        token_counts=TokenCountSchema(**token_counts),
        metadata={"token_counts": token_counts, **data.metadata} if data.metadata else {"token_counts": token_counts}
    )

@kitchen.storage.handler("storage")
async def storage_handler(data: WhiskStorageSchema) -> WhiskStorageResponseSchema:
    """Storage handler for document ingestion"""
    try:
        # Create a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Use the original filename for the temporary file
            temp_file_path = Path(temp_dir) / Path(data.name).name
            
            # Write bytes data to temporary file
            with open(temp_file_path, 'wb') as f:
                f.write(data.data)
            
            # Initialize parser and load the file
            parser = Parser(api_key=os.environ.get("LLAMA_CLOUD_API_KEY", None))
            response = parser.load(str(temp_dir), metadata=data.metadata)
            
            # Setup storage context and process documents
            storage_context = StorageContext.from_defaults(vector_store=vector_store)
            
            # Create index with transformations
            VectorStoreIndex.from_documents(
                response["documents"],
                storage_context=storage_context,
                transformations=[
                    TokenTextSplitter(),
                    TitleExtractor(),
                    QuestionsAnsweredExtractor()
                ],
                show_progress=True
            )
            

            return WhiskStorageResponseSchema(
                id=data.id,
                name=data.name,
                label=data.label,
                data=data.data,
            )
            
    except Exception as e:
        logger.error(f"Error in storage handler: {str(e)}")
        raise

@kitchen.storage.on_delete("storage")
async def storage_delete_handler(data: WhiskStorageSchema) -> None:
    """Storage delete handler"""
    logger.info(f"Deleting storage for {data.id}")


@kitchen.embeddings.handler("embed")
async def embed_handler(data: WhiskEmbedSchema) -> WhiskEmbedResponseSchema:
    """Embedding handler"""
    try:
        # Create document and index it
        document = Document(text=data.text, metadata=data.metadata)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        
        VectorStoreIndex.from_documents(
            [document],
            storage_context=storage_context,
            transformations=[
                TokenTextSplitter(),
                TitleExtractor(),
                QuestionsAnsweredExtractor()
            ],
            show_progress=True
        )

        token_counts = {
            "embedding_tokens": token_counter.total_embedding_token_count,
            "llm_prompt_tokens": token_counter.prompt_llm_token_count,
            "llm_completion_tokens": token_counter.completion_llm_token_count,
            "total_llm_tokens": token_counter.total_llm_token_count
        }
        token_counter.reset_counts()

        return WhiskEmbedResponseSchema(
            text=data.text,
            token_counts=TokenCountSchema(**token_counts),
            metadata={"token_counts": token_counts, **data.metadata} if data.metadata else {"token_counts": token_counts}
        )
    except Exception as e:
        logger.error(f"Error in embed handler: {str(e)}")
        raise

if __name__ == "__main__":
    client = WhiskClient(
        nats_url="nats://localhost:4222",
        client_id="llama-index",
        user="playground",
        password="kitchenai_playground",
        kitchen=kitchen,
    )
    
    async def start():
        await client.run()

    try:
        asyncio.run(start())
    except KeyboardInterrupt:
        logger.info("\nShutting down gracefully...")
