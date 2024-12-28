
from ninja import Router
from pydantic import BaseModel
from ninja.errors import HttpError
from django.http import HttpResponse
import logging
from django.apps import apps
from ..signals import query_output_signal, query_input_signal
from kitchenai.contrib.kitchenai_sdk.schema import QuerySchema, QueryBaseResponseSchema
from uuid import uuid4
from django_eventstream import send_event

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
        core_app = apps.get_app_config("core")
        if not core_app.kitchenai_app:
            logger.error("No kitchenai app in core app config")
            raise HttpError(404, "No kitchenai app in core app config")
        
        query_func = core_app.kitchenai_app.query.get_task(label)
        if not query_func:
            logger.error(f"Query function not found for {label}")
            raise HttpError(404, "Query function not found for {label}")
        
        #Signal the start of the query. Generic signals
        query_input_signal.send(sender="pre_query", data=data)
        if data.stream:
            if not data.stream_id:
                logger.error("stream_id is required for streaming requests")
                raise HttpError(400, "stream_id is required for streaming requests")
            
            results = await query_func(data)
            if results.stream_gen:
                # If it's an async generator, we need to handle it differently
                if not hasattr(results.stream_gen, '__aiter__'):
                    logger.error("Expected async generator but received different type")
                    raise HttpError(500, "Internal streaming error")
                logger.debug(f"streaming text: {data.stream_id}")
                async for text in results.stream_gen:
                    # Yield each chunk of text as it arrives
                    send_event(data.stream_id, "message", text)
                metadata = KitchenAIMetadata(stream_id=data.stream_id, stream=data.stream)

                return QueryResponseSchema(kitchenai_metadata=metadata)
            metadata = KitchenAIMetadata(stream_id=data.stream_id, stream=data.stream)
            return QueryResponseSchema(kitchenai_metadata=metadata)
        
        result = await query_func(data)
        #Signal the end of the query
        metadata = KitchenAIMetadata(stream=data.stream)
        extended_result = QueryResponseSchema(**result.dict(), kitchenai_metadata=metadata)
        query_output_signal.send(sender="post_query", result=extended_result)
        return extended_result
    except HttpError as e:
        logger.error(f"HttpError raised: {e}")
        raise e  
    except Exception as e:
        logger.error(f"Error in query: {e}")
        raise HttpError(500, "query function not found")
