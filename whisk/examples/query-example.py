# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "kitchenai-whisk",
#   "llama-index",
# ]
# ///

from whisk.kitchenai_sdk.kitchenai import KitchenAIApp
from whisk.kitchenai_sdk.schema import QuerySchema, QueryBaseResponseSchema
from llama_index.llms.openai import OpenAI
import logging
import asyncio
from whisk.client import WhiskClient
# Initialize LLM and embeddings
llm = OpenAI(model="gpt-3.5-turbo")

kitchen = KitchenAIApp(namespace="example_query")

# pip install llama-index
logger = logging.getLogger(__name__)


@kitchen.query.handler("query")
async def query_handler(data: QuerySchema) -> QueryBaseResponseSchema:
    """Query handler"""

    response = await llm.acomplete(data.query)

    print(response)

    return QueryBaseResponseSchema.from_llm_invoke(
        data.query,
        response.text,
    )

if __name__ == "__main__":

    client = WhiskClient(
        nats_url="nats://localhost:4222",
        client_id="whisk_client",
        user="playground",
        password="kitchenai_playground",
        kitchen=kitchen,
    )
    async def start():
        await client.app.run()

    try:
        asyncio.run(start())
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
