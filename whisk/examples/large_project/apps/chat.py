from whisk.kitchenai_sdk.kitchenai import KitchenAIApp
from whisk.kitchenai_sdk.schema import WhiskQuerySchema, WhiskQueryBaseResponseSchema

chat_app = KitchenAIApp(namespace="chat")

@chat_app.query.handler("basic")
async def basic_chat(data: WhiskQuerySchema, llm=None):
    """Basic chat handler"""
    ...

@chat_app.query.handler("stream")
async def stream_chat(data: WhiskQuerySchema, llm=None):
    """Streaming chat handler"""
    ... 