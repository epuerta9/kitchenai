from django.http import HttpRequest
from django.template.response import TemplateResponse
from django.conf import settings
from django.apps import apps
from django.http import HttpResponse
from kitchenai.core.exceptions import QueryHandlerBadRequestError
from kitchenai.core.api.query import whisk_query
from kitchenai.core.signals.query import QuerySignalSender, query_signal
from whisk.kitchenai_sdk.schema import WhiskQuerySchema
from collections import deque
import logging
import json
from datetime import datetime
from django.http import HttpResponseRedirect
from kitchenai.apps.utils import hash_to_int

logger = logging.getLogger(__name__)

MAX_CHAT_HISTORY = 10
BentoClient = apps.get_model(settings.KITCHENAI_BENTO_CLIENT_MODEL)

async def chat_send(request: HttpRequest):
    """Handle chat messages in the playground with session-based history."""
    message = request.POST.get("message")
    selected_bento_client_id = request.POST.get("selected_bento_id")

    if not all([message, selected_bento_client_id]):
        return TemplateResponse(
            request, 
            "apps/playground/includes/chat_response.html", 
            {"error": "Missing required parameters"}
        )
    logger.info(f"selected_bento_client_id: {selected_bento_client_id}")
    #get the selected bento
    selected_bento = await BentoClient.objects.filter(
        id=int(selected_bento_client_id),
        ack=True
    ).afirst()

    if not selected_bento:
        return TemplateResponse(
            request, 
            "apps/playground/includes/chat_response.html", 
            {"error": "Bento not found"}
        )

    #lets make sure the client id is either part of the session of the allowed bentos
    allowed_bento_ids = await request.session.aget('allowed_bento_ids', [])
    client_id = await request.session.aget('client_id', None)
    if client_id:
        #get bento from db with client_id
        client_bento = await BentoClient.objects.filter(
            client_id=client_id,
            ack=True
        ).afirst()
        if client_bento:
            allowed_bento_ids.append(client_bento.id)

    if selected_bento.id not in allowed_bento_ids:
        return TemplateResponse(
            request, 
            "apps/playground/includes/chat_response.html", 
            {"error": "Bento not allowed"}
        )
    logger.info(f"selected_bento: {selected_bento.client_id}")
    try:
        result = await whisk_query(
            selected_bento.client_id,
            "query",
            WhiskQuerySchema(
                query=message,
                stream=False,
                metadata={"environment": "playground"}
            )
        )

    except Exception as e:
        logger.error(f"Error in chat_send: {str(e)}")
        return TemplateResponse(
            request, 
            "apps/playground/includes/chat_response.html", 
            {"message": message, "error": str(e)}
        )

    # Convert retrieval context to JSON-serializable format
    sources = [
        {
            "text": source.text,
            "metadata": source.metadata,
            "score": source.score
        }
        for source in (result.retrieval_context or [])
    ]

    # Create metrics dictionary
    current_metrics = {
        "input_text": result.input,
        "output_text": result.output,
        "metadata": result.metadata or {},
        "sources_used": sources,
        "timestamp": datetime.now().isoformat(),
    }

    if result.token_counts:
        current_metrics.update({
            "embedding_tokens": result.token_counts.embedding_tokens,
            "llm_prompt_tokens": result.token_counts.llm_prompt_tokens,
            "llm_completion_tokens": result.token_counts.llm_completion_tokens,
            "total_llm_tokens": result.token_counts.total_llm_tokens,
        })

    # Get existing chat history from session or initialize empty list
    chat_history = await request.session.aget('chat_history', [])
    
    # Add new interaction to history
    chat_history.append(current_metrics)
    
    # Keep only the last MAX_CHAT_HISTORY interactions
    if len(chat_history) > MAX_CHAT_HISTORY:
        chat_history = chat_history[-MAX_CHAT_HISTORY:]
    
    # Update session
    await request.session.aset('chat_history', chat_history)

    # Generate message_id from timestamp
    message_id = hash_to_int(current_metrics['timestamp'])



    # Return chat response template
    return TemplateResponse(
        request,
        "apps/playground/includes/chat_response.html",
        {
            "metrics": current_metrics,
            "message_id": message_id,
        },
    )

async def clear_chat_history(request: HttpRequest) -> HttpResponse:
    """Clear the chat history from the session."""
    await request.session.aset('chat_history', [])
    request.session.modified = True
    
    # Return empty state template for HTMX
    return TemplateResponse(
        request,
        "apps/playground/includes/empty_chat.html",
        {
            "selected_bento": await request.session.aget('selected_bento')
        }
    )
