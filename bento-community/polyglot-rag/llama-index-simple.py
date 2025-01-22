# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "kitchenai-whisk",
#   "llama-index",
#   "tiktoken"
# ]
# ///

from whisk.kitchenai_sdk.kitchenai import KitchenAIApp
from whisk.kitchenai_sdk.schema import (
    WhiskQuerySchema,
    WhiskQueryBaseResponseSchema,
)

from llama_index.llms.openai import OpenAI
from llama_index.core.callbacks import CallbackManager, TokenCountingHandler
from llama_index.core import Settings
import logging
import asyncio
import tiktoken
from whisk.client import WhiskClient

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

# Initialize KitchenAI App
kitchen = KitchenAIApp(namespace="llama-index-simple")

@kitchen.query.handler("query")
async def query_handler(data: WhiskQuerySchema) -> WhiskQueryBaseResponseSchema:
    """Simple LLM query handler"""
    try:
        # Execute query using llm.acomplete
        response = await llm.acomplete(data.query)

        # Get token counts
        token_counts = {
            "llm_prompt_tokens": token_counter.prompt_llm_token_count,
            "llm_completion_tokens": token_counter.completion_llm_token_count,
            "total_llm_tokens": token_counter.total_llm_token_count
        }
        token_counter.reset_counts()

        return WhiskQueryBaseResponseSchema.from_llm_invoke(
            data.query,
            response.text,
            metadata={"token_counts": token_counts, **data.metadata} if data.metadata else {"token_counts": token_counts}
        )
    except Exception as e:
        logger.error(f"Error in query handler: {str(e)}")
        raise

if __name__ == "__main__":
    client = WhiskClient(
        nats_url="nats://localhost:4222",
        client_id="llama-index-simple",
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
