from whisk.kitchenai_sdk.kitchenai import KitchenAIApp
from whisk.kitchenai_sdk.schema import (
    WhiskQuerySchema,
    WhiskQueryBaseResponseSchema,
    TokenCountSchema
)

from openai import AsyncOpenAI
import tiktoken
import logging
import asyncio
from whisk.client import WhiskClient

# Setup logging
logger = logging.getLogger(__name__)

# Initialize OpenAI client
openai_client = AsyncOpenAI()

# Initialize tokenizer for counting
encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")

# Initialize KitchenAI App
kitchen = KitchenAIApp(namespace="openai-simple")

@kitchen.query.handler("query")
async def query_handler(data: WhiskQuerySchema) -> WhiskQueryBaseResponseSchema:
    """Simple OpenAI query handler"""
    try:
        # Create chat completion
        response = await openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": data.query}
            ]
        )
        
        # Extract response text
        response_text = response.choices[0].message.content

        # Get token counts
        token_counts = {
            "llm_prompt_tokens": response.usage.prompt_tokens,
            "llm_completion_tokens": response.usage.completion_tokens,
            "total_llm_tokens": response.usage.total_tokens
        }

        return WhiskQueryBaseResponseSchema.from_llm_invoke(
            data.query,
            response_text,
            token_counts=TokenCountSchema(**token_counts),
            metadata={"token_counts": token_counts, **data.metadata} if data.metadata else {"token_counts": token_counts}
        )
    except Exception as e:
        logger.error(f"Error in query handler: {str(e)}")
        raise

if __name__ == "__main__":
    client = WhiskClient(
        nats_url="nats://localhost:4222",
        client_id="openai-simple",
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