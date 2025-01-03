
from ninja import Router
from pydantic import BaseModel
from ninja.errors import HttpError
import logging
from django.apps import apps
from ..signals import query_signal, QuerySignalSender
from kitchenai.contrib.kitchenai_sdk.schema import QuerySchema, QueryBaseResponseSchema
from django_eventstream import send_event
from kitchenai.core.exceptions import QueryHandlerBadRequestError

logger = logging.getLogger(__name__)
router = Router()

class KitchenAIMetadata(BaseModel):
    stream_id: str | None = None
    stream: bool

class QueryResponseSchema(QueryBaseResponseSchema):
    kitchenai_metadata: KitchenAIMetadata | None = None

@router.post("/{label}", response=QueryResponseSchema)
async def query(request, label: str, data: QuerySchema):
    """Create a new query"""
    """process file async function for core app using storage task"""
    try:
        await query_signal.asend(sender=QuerySignalSender.PRE_API_QUERY, data=data)
        result = await query_handler(label, data)
        if not result.sources:
            await query_signal.asend(sender=QuerySignalSender.POST_API_QUERY, result=result, error=True)
        else:
            await query_signal.asend(sender=QuerySignalSender.POST_API_QUERY, result=result)
        return result
    except QueryHandlerBadRequestError as e:
        logger.error(f"QueryHandlerBadRequestError raised: {e}")
        raise HttpError(400, e.message)
    except Exception as e:
        logger.error(f"Error in <api/query>: {e}")
        raise HttpError(500, "query function not found")


async def query_handler(label: str, data: QuerySchema) -> QueryResponseSchema:
    try:
        core_app = apps.get_app_config("core")
        if not core_app.kitchenai_app:
            logger.error("No kitchenai app in core app config")
            raise QueryHandlerBadRequestError(message="No kitchenai app in core app config")
        
        query_func = core_app.kitchenai_app.query.get_task(label)
        if not query_func:
            logger.error(f"Query function not found for {label}")
            raise QueryHandlerBadRequestError(message=f"Query function not found for {label}")
        
        #Signal the start of the query. Generic signals
        if data.stream:
            if not data.stream_id:
                logger.error("stream_id is required for streaming requests")
                raise QueryHandlerBadRequestError(message="stream_id is required for streaming requests")
            
            results = await query_func(data)
            if results.stream_gen:
                # If it's an async generator, we need to handle it differently
                if not hasattr(results.stream_gen, '__aiter__'):
                    logger.error("Expected async generator but received different type")
                    raise QueryHandlerBadRequestError(message="Internal streaming error")
                
                async for text in results.stream_gen:

                    send_event(data.stream_id, "message", {"output": text})
                send_event(data.stream_id, "stream-end", {"output": "Stream complete"})

                metadata = KitchenAIMetadata(stream_id=data.stream_id, stream=data.stream)

                return QueryResponseSchema(kitchenai_metadata=metadata)
            metadata = KitchenAIMetadata(stream_id=data.stream_id, stream=data.stream)
            return QueryResponseSchema(kitchenai_metadata=metadata)
        
        result = await query_func(data)
        #Signal the end of the query
        metadata = KitchenAIMetadata(stream=data.stream)
        extended_result = QueryResponseSchema(**result.dict(), kitchenai_metadata=metadata)
        return extended_result
    except Exception as e:
        logger.error(f"Error in query handler: {e}")
        raise QueryHandlerBadRequestError(message="query handler not found")
