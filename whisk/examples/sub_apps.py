from whisk.kitchenai_sdk.kitchenai import KitchenAIApp
from whisk.kitchenai_sdk.schema import (
    WhiskQuerySchema, 
    WhiskQueryBaseResponseSchema,
    DependencyType
)

# Create sub-apps for different components
chat_app = KitchenAIApp(namespace="chat")
rag_app = KitchenAIApp(namespace="rag")
tools_app = KitchenAIApp(namespace="tools")

# Register handlers to sub-apps
@chat_app.query.handler("basic")
async def basic_chat(data: WhiskQuerySchema, llm=None) -> WhiskQueryBaseResponseSchema:
    """Basic chat handler"""
    ...

@rag_app.query.handler("search")
async def rag_search(data: WhiskQuerySchema, llm=None, vector_store=None) -> WhiskQueryBaseResponseSchema:
    """RAG search handler"""
    ...

@tools_app.query.handler("calculator")
async def calculator(data: WhiskQuerySchema, llm=None) -> WhiskQueryBaseResponseSchema:
    """Calculator tool"""
    ...

# Create main app and mount sub-apps
main_app = KitchenAIApp(namespace="main")
main_app.mount_app("chat", chat_app)  # Will create handlers like "chat.basic"
main_app.mount_app("rag", rag_app)    # Will create handlers like "rag.search"
main_app.mount_app("tools", tools_app) # Will create handlers like "tools.calculator"

# The resulting NATS subjects would be:
# - kitchenai.service.{client_id}.query.chat.basic
# - kitchenai.service.{client_id}.query.rag.search
# - kitchenai.service.{client_id}.query.tools.calculator 