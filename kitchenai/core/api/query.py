
from ninja import Router
from ninja import Schema
from ninja.errors import HttpError
from ninja import Schema
from django.http import HttpResponse
import logging
from django.apps import apps
from ..signals import query_output_signal, query_input_signal


logger = logging.getLogger(__name__)
router = Router()

class QuerySchema(Schema):
    query: str
    metadata: dict[str, str] | None = None

class QueryResponseSchema(Schema):
    response: str

class AgentResponseSchema(Schema):
    response: str


@router.post("/{label}", response=QueryResponseSchema)
async def query(request, label: str, data: QuerySchema):
    """Create a new query"""
    """process file async function for core app using storage task"""
    try:
        core_app = apps.get_app_config("core")
        if not core_app.kitchenai_app:
            logger.error("No kitchenai app in core app config")
            return HttpResponse(status=404)
        
        query_func = core_app.kitchenai_app._query_handlers.get(f"{core_app.kitchenai_app._namespace}.{label}")
        if not query_func:
            logger.error(f"Query function not found for {label}")
            return HttpResponse(status=404)
        
        #Signal the start of the query
        query_input_signal.send(sender="query_input", data=data)
        result = await query_func(data)
        #Signal the end of the query
        query_output_signal.send(sender="query_output", result=result)
        return result
    except Exception as e:
        logger.error(f"Error in query: {e}")
        return HttpError(500, "query function not found")