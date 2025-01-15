from whisk.kitchenai_sdk.kitchenai import KitchenAIApp
from whisk.kitchenai_sdk.schema import QuerySchema, QueryBaseResponseSchema
import logging

kitchen = KitchenAIApp(namespace="kitchenai_rag_simple_bento")

logger = logging.getLogger(__name__)
@kitchen.query.handler("query")
async def kitchenai_bento_simple_rag_vjnk(data: QuerySchema) -> QueryBaseResponseSchema:
    """Query handler"""

    response = "Hello World again"

    return QueryBaseResponseSchema.from_response(data, response, metadata=data.metadata)

