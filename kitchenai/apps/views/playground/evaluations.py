import json
from django.http import HttpRequest, HttpResponse
from django.template.response import TemplateResponse
from django.conf import settings
from kitchenai.core.signals import query_signal, QuerySignalSender
from whisk.kitchenai_sdk.schema import WhiskQueryBaseResponseSchema, SourceNodeSchema
import logging
from django.apps import apps
import hashlib

logger = logging.getLogger(__name__)

def hash_uuid_to_int(uuid_string: str) -> int:
    """Convert a UUID string to a positive integer using hash."""
    # Take first 8 characters of hash to keep number manageable
    hash_hex = hashlib.md5(uuid_string.encode()).hexdigest()[:8]
    return int(hash_hex, 16)  # Convert hex to int

async def evaluate_response(request: HttpRequest) -> HttpResponse:
    """Handle evaluation of chat responses."""
    try:
        # Get the last chat message from session history
        chat_history = await request.session.aget("chat_history", [])
        if not chat_history:
            raise ValueError("No chat history found")

        current_metrics = chat_history[-1]  # Get the last message

        user_uuid = await request.session.aget("anonymous_id", None)
        if not user_uuid:
            raise ValueError("No anonymous user id found")
        
        # Convert UUID to integer for source_id
        user_id = hash_uuid_to_int(user_uuid)
        
        logger.info(f"user_uuid: {user_uuid}, hashed_id: {user_id}")

        # Convert sources to SourceNodeSchema format
        source_nodes = [
            SourceNodeSchema(
                text=source["text"],
                metadata=source["metadata"],
                score=source["score"]
            ) for source in current_metrics["sources_used"]
        ]

        # Create WhiskQueryBaseResponseSchema
        result = WhiskQueryBaseResponseSchema(
            input=current_metrics["input_text"],
            output=current_metrics["output_text"],
            retrieval_context=source_nodes,
            metadata=current_metrics.get("metadata", {}),
            token_counts=current_metrics.get("token_counts", None)
        )

        # Send signal with model_dump
        if not current_metrics["sources_used"]:
            await query_signal.asend(
                QuerySignalSender.POST_DASHBOARD_QUERY,
                **result.model_dump(),
                source_id=user_id,
                error=True
            )
        else:
            await query_signal.asend(
                QuerySignalSender.POST_DASHBOARD_QUERY,
                **result.model_dump(),
                source_id=user_id
            )

        # Get plugin widgets only for deepeval_plugin
        plugin_widgets = []
        plugins = settings.KITCHENAI.get("plugins", [])
        if plugins:
            plugin_objects = [
                apps.get_app_config(plugin["name"])
                for plugin in plugins
                if plugin["name"] == "deepeval_plugin"
            ]
            for plugin in plugin_objects:
                plugin_widgets.append(plugin.plugin.get_chat_metric_widget())

        return TemplateResponse(
            request,
            "apps/playground/includes/metrics_section.html",
            {
                "user_id": user_id, 
                "plugin_widgets": plugin_widgets, 
                "has_results": True,
                "chat_history": chat_history,  # Pass chat_history to keep button visible
                "current_metrics": current_metrics
            },
        )
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return HttpResponse(
            '<button class="btn btn-ghost btn-xs tooltip tooltip-right" '
            'data-tip="No chat history found">'
            '<svg data-src="https://unpkg.com/heroicons/20/solid/x-circle.svg" '
            'class="h-4 w-4 text-error"></svg>'
            "</button>"
        )
    except Exception as e:
        logger.error(f"Error during evaluation: {e}")
        return HttpResponse(
            '<button class="btn btn-ghost btn-xs tooltip tooltip-right" '
            'data-tip="Evaluation failed">'
            '<svg data-src="https://unpkg.com/heroicons/20/solid/x-circle.svg" '
            'class="h-4 w-4 text-error"></svg>'
            "</button>"
        )
