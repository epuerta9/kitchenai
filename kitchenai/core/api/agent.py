
from ninja import Router
from ninja import Schema
from ninja.errors import HttpError
from ninja import Schema
from django.http import HttpResponse
import logging
import posthog
from django.apps import apps
from kitchenai.contrib.kitchenai_sdk.schema import QuerySchema, AgentResponseSchema


logger = logging.getLogger(__name__)
router = Router()



@router.post("/{label}", response=AgentResponseSchema)
async def agent(request, label: str, data: QuerySchema):
    """Create a new agent"""
    try:
        posthog.capture("kitchenai_sdk", "agent_handler")
        core_app = apps.get_app_config("core")
        if not core_app.kitchenai_app:
            logger.error("No kitchenai app in core app config")
            return HttpResponse(status=404)
        agent_func = core_app.kitchenai_app.agents.get_task(label)
        if not agent_func:
            logger.error(f"Agent function not found for {label}")
            return HttpResponse(status=404)

        return await agent_func(data)
    except Exception as e:      
        logger.error(f"Error in agent: {e}")
        return HttpError(500, "agent function not found")