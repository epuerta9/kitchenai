# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "kitchenai-whisk",
#   "langchain",
#   "langchain-openai",
#   "langchain-community",
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
)

import logging
import asyncio
import tiktoken
from whisk.client import WhiskClient

# Setup logging
logger = logging.getLogger(__name__)

# Initialize token counter
encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")

# Import and initialize LangChain components after logging setup
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
import chromadb

# Initialize LLM and embeddings
llm = ChatOpenAI(model="gpt-3.5-turbo", verbose=True)
embeddings = OpenAIEmbeddings()

# Initialize Vector Store
chroma_client = chromadb.PersistentClient(path="chroma_db")
vector_store = Chroma(
    client=chroma_client,
    collection_name="quickstart",
    embedding_function=embeddings
)

# Initialize text splitter
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)

# Setup RAG prompt
template = """Answer the question based on the following context:

Context: {context}

Question: {question}

Answer: """

prompt = ChatPromptTemplate.from_template(template)

# Initialize KitchenAI App
kitchen = KitchenAIApp(namespace="langchain")

@kitchen.query.handler("query")
async def query_handler(data: WhiskQuerySchema) -> WhiskQueryBaseResponseSchema:
    """Query handler with RAG"""
    try:
        # Create retriever with metadata filtering if provided
        if data.metadata:
            retriever = vector_store.as_retriever(
                search_kwargs={"filter": data.metadata}
            )
        else:
            retriever = vector_store.as_retriever()

        # Create RAG chain
        rag_chain = (
            {"context": retriever, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )

        # Execute query
        response = await rag_chain.ainvoke(data.query)

        # Calculate token usage (approximate)
        prompt_tokens = len(encoding.encode(template + data.query))
        completion_tokens = len(encoding.encode(response))
        
        token_counts = {
            "embedding_tokens": 0,  # Embeddings tokens not directly accessible in langchain
            "llm_prompt_tokens": prompt_tokens,
            "llm_completion_tokens": completion_tokens,
            "total_llm_tokens": prompt_tokens + completion_tokens
        }

        return WhiskQueryBaseResponseSchema.from_llm_invoke(
            data.query,
            response,
            metadata={"token_counts": token_counts, **data.metadata} if data.metadata else {"token_counts": token_counts}
        )
    except Exception as e:
        logger.error(f"Error in query handler: {str(e)}")
        raise

@kitchen.storage.handler("storage")
async def storage_handler(data: WhiskStorageSchema) -> WhiskStorageResponseSchema:
    """Storage handler for document ingestion"""
    try:
        # Create documents from the input data
        documents = [
            Document(page_content=text, metadata=data.metadata or {})
            for text in data.data
        ]

        # Split documents
        split_docs = text_splitter.split_documents(documents)
        
        # Add to vector store
        vector_store.add_documents(split_docs)

        # Calculate token usage (approximate)
        total_tokens = sum(len(encoding.encode(doc.page_content)) for doc in split_docs)
        
        token_counts = {
            "embedding_tokens": total_tokens,
            "llm_prompt_tokens": 0,
            "llm_completion_tokens": 0,
            "total_llm_tokens": 0
        }

        return WhiskStorageResponseSchema(
            id=data.id,
            data=data.data,
            metadata={"token_counts": token_counts, **data.metadata} if data.metadata else {"token_counts": token_counts}
        )
    except Exception as e:
        logger.error(f"Error in storage handler: {str(e)}")
        raise

@kitchen.embeddings.handler("embed")
async def embed_handler(data: WhiskEmbedSchema) -> WhiskEmbedResponseSchema:
    """Embedding handler"""
    try:
        # Create document
        document = Document(
            page_content=data.text,
            metadata=data.metadata or {}
        )

        # Split if necessary
        split_docs = text_splitter.split_documents([document])
        
        # Add to vector store
        vector_store.add_documents(split_docs)

        # Calculate token usage (approximate)
        total_tokens = sum(len(encoding.encode(doc.page_content)) for doc in split_docs)
        
        token_counts = {
            "embedding_tokens": total_tokens,
            "llm_prompt_tokens": 0,
            "llm_completion_tokens": 0,
            "total_llm_tokens": 0
        }

        return WhiskEmbedResponseSchema(
            text=data.text,
            metadata={"token_counts": token_counts, **data.metadata} if data.metadata else {"token_counts": token_counts}
        )
    except Exception as e:
        logger.error(f"Error in embed handler: {str(e)}")
        raise

if __name__ == "__main__":
    client = WhiskClient(
        nats_url="nats://localhost:4222",
        client_id="langchain",
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
