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
from django.http import StreamingHttpResponse
import re
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
        if data.stream:
            result = await query_handler(label, data)
            
            async def event_stream():
                async def query_response_stream():
                    async def chunk_stream():
                        buffer = ""  # Hold partial chunks to assemble words

                        async for chunk in result.stream_gen:
                            buffer += chunk  # Collect incoming data
                            # Use regex to detect words ending with space or punctuation
                            words = re.findall(r"\b[\w']+(?:[.,!?])?|\S", buffer)

                            # Check if the last chunk is incomplete (no space or punctuation yet)
                            if buffer and not buffer[-1].isspace() and buffer[-1] not in ",.?!":
                                # Hold the last partial word back in the buffer for the next chunk
                                buffer = words.pop() if words else ""
                            else:
                                buffer = ""

                            # Stream only complete words
                            for word in words:
                                yield f"{word}\n\n".encode('utf-8')

                        # Send any remaining buffer as the final word
                        if buffer.strip():
                            yield f"{buffer.strip()}\n\n".encode('utf-8')
                    
                    async for word in chunk_stream():
                        yield QueryResponseSchema(input=data.query, output=word, sources=[], metadata=data.metadata, kitchenai_metadata=KitchenAIMetadata(stream_id=data.stream_id, stream=data.stream))

                async for query_response in query_response_stream():
                    yield query_response


            response = StreamingHttpResponse(event_stream(), content_type='text/event-stream')
            response['Cache-Control'] = 'no-cache'
            return response
        else:
            result = await query_handler(label, data)
            if not result.retrieval_context:
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
        
        result = await query_func(data)
        #Signal the end of the query
        metadata = KitchenAIMetadata(stream=data.stream)
        extended_result = QueryResponseSchema(**result.dict(), kitchenai_metadata=metadata)
        return extended_result
    except Exception as e:
        logger.error(f"Error in query handler: {e}")
        raise QueryHandlerBadRequestError(message="query handler not found")
