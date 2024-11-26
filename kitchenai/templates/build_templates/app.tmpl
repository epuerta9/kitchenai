from kitchenai.contrib.kitchenai_sdk.kitchenai import KitchenAIApp

from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.vector_stores.chroma import ChromaVectorStore
from kitchenai.contrib.kitchenai_sdk.api import QuerySchema, EmbedSchema
from llama_index.llms.openai import OpenAI
import os 
import chromadb
from llama_index.llms.openai import OpenAI
from kitchenai.contrib.kitchenai_sdk.storage.llama_parser import Parser
from llama_index.core.node_parser import TokenTextSplitter
from llama_index.core.extractors import (
    TitleExtractor,
    QuestionsAnsweredExtractor)

from llama_index.core import Document

from llama_stack_client import AsyncLlamaStackClient
from llama_stack_client.types import UserMessage
from llama_stack_client import LlamaStackClient


from llama_stack_client.lib.agents.agent import Agent
from llama_stack_client.types.agent_create_params import AgentConfig


# create client and a new collection
chroma_client = chromadb.PersistentClient(path="chroma_db")
chroma_collection = chroma_client.get_or_create_collection("quickstart")
client = AsyncLlamaStackClient(
    base_url=f"http://localhost:5000",
)
client_sync = LlamaStackClient(
    base_url=f"http://localhost:5000",
)

llm = OpenAI(model="gpt-4")

kitchen = KitchenAIApp()

import logging

logger = logging.getLogger(__name__)

@kitchen.storage("file")
def chromadb_storage(dir: str, metadata: dict = {}, *args, **kwargs):
    """
    Store uploaded files into a vector store with metadata
    """
    parser = Parser(api_key=os.environ.get("LLAMA_CLOUD_API_KEY", None))

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


@kitchen.embed("embed")
def embed(instance, metadata: dict = {}):
    """Embed single pieces of text"""
    documents = [Document(text=instance.text)]
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

    storage_context = StorageContext.from_defaults(vector_store=vector_store)
            
    VectorStoreIndex.from_documents(
        documents, storage_context=storage_context, show_progress=True,
            transformations=[TokenTextSplitter(), TitleExtractor(),QuestionsAnsweredExtractor()]
    )
    return "ok"


@kitchen.query("simple-query")
async def query(request, data: QuerySchema):
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

    index = VectorStoreIndex.from_vector_store(
        vector_store,
    )
    query_engine = index.as_query_engine(chat_mode="best", llm=llm, verbose=True)
    response = await query_engine.aquery(data.query)

    print(response)

    return {"msg": response.response}


@kitchen.query("chat")
async def query_chat(request, data: QuerySchema):

    response = await client.inference.chat_completion(
        model_id="meta-llama/Llama-3.2-3B-Instruct",
        messages=[
            UserMessage(
                content="hello world, write me a 2 sentence poem about the moon",
                role="user",
            ),
        ],
        stream=False,
    )

    print(response.completion_message.content)

    return {"msg": response.completion_message.content}


@kitchen.query("agent-create")
def query_chat(request, data: QuerySchema):

    agent_config = AgentConfig(
        model="meta-llama/Llama-3.2-3B-Instruct",
        instructions="You are a helpful assistant",
        sampling_params={
            "strategy": "greedy",
            "temperature": 1.0,
            "top_p": 0.9,
        },
        tools=[
            {
                "type": "brave_search",
                "engine": "brave",
                "api_key": os.getenv("BRAVE_SEARCH_API_KEY"),
            }
        ],
        tool_choice="auto",
        tool_prompt_format="function_tag",
        enable_session_persistence=False,
    )
    agent = Agent(client_sync, agent_config)
    session_id = agent.create_session("test-session")

    print(f"Created session_id={session_id} for Agent({agent.agent_id})")


    response = agent.create_turn(
            messages=[
                {
                    "role": "user",
                    "content": "I am planning a trip to Switzerland, what are the top 3 places to visit?",
                }
            ],
            session_id=session_id,
        )

    print(dir(response))
    for event in response:
        print(dir(event))
        print(event)

    return {"msg": "ok"}