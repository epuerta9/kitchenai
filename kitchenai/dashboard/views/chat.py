from django.http import HttpRequest
from django.template.response import TemplateResponse
from django.conf import settings
from kitchenai.bento.models import Bento
from kitchenai.core.models import KitchenAIManagement
from django.shortcuts import redirect
from django.apps import apps
from django.http import HttpResponse
from ..models import Chat, ChatMetric, AggregatedChatMetric, ChatSetting
from kitchenai.core.exceptions import QueryHandlerBadRequestError
from kitchenai.contrib.kitchenai_sdk.schema import QuerySchema
from kitchenai.core.api.query import query_handler
from kitchenai.core.signals.query import QuerySignalSender, query_signal
from django.contrib.auth.decorators import login_required
import logging

logger = logging.getLogger(__name__)

@login_required
async def chat(request: HttpRequest):
    if request.method == "POST":
        mgmt = await KitchenAIManagement.objects.filter(
            name="kitchenai_management"
        ).afirst()
        if mgmt.module_path == "bento":
            name = await Bento.objects.afirst()
        else:
            name = mgmt.module_path
        chat = await Chat.objects.acreate(name=name)
        labels = apps.get_app_config("core")
        if labels:
            labels = labels.kitchenai_app.to_dict()
        else:
            return TemplateResponse(request, "dashboard/pages/errors.html", {"error": "No query handlers found"})
        if labels["query_handlers"]:
            await ChatSetting.objects.acreate(chat=chat, selected_label=labels["query_handlers"][0], bento_name=name, chat_type=ChatSetting.ChatType.QUERY)
        else:
           return TemplateResponse(request, "dashboard/pages/errors.html", {"error": "No query handlers found"})
        return redirect("dashboard:chat_session", chat_id=chat.id)

    chats = Chat.objects.all()
    return TemplateResponse(request, "dashboard/pages/chat.html", {"chats": chats})


@login_required
async def chat_session(request: HttpRequest, chat_id: int):
    plugin_widgets = []
    plugins = settings.KITCHENAI.get("plugins", [])
    if plugins:
        #get the plugin objects from app configs 
        plugin_objects = [apps.get_app_config(plugin["name"]) for plugin in plugins]
        for plugin in plugin_objects:
            plugin_widgets.append(plugin.plugin.get_chat_metric_widget())

    chat = (
        await Chat.objects.select_related("chatsetting")
        .prefetch_related(
            "chatmetric_set",
        )
        .aget(id=chat_id)
    )

    all_metrics = list(chat.chatmetric_set.all())

    return TemplateResponse(
        request,
        "dashboard/pages/chat_session.html",
        {
            "chat": chat,
            "metrics": all_metrics,
            "settings": chat.chatsetting,
            "plugin_widgets": plugin_widgets,
        },
    )

@login_required
async def chat_delete(request: HttpRequest, chat_id: int):
    await Chat.objects.filter(id=chat_id).adelete()
    return HttpResponse("")


@login_required
async def aggregated_metrics(request: HttpRequest, chat_id: int):
    chat = await Chat.objects.aget(id=chat_id)
    try:
        aggregated = await AggregatedChatMetric.objects.aget(chat=chat)
        return TemplateResponse(
            request,
            "dashboard/htmx/aggregated_metrics.html",
            {"aggregated": aggregated},
        )
    except AggregatedChatMetric.DoesNotExist:
        return TemplateResponse(
            request, "dashboard/htmx/aggregated_metrics.html", {"aggregated": None}
        )
    
@login_required
async def chat_settings(request: HttpRequest, chat_id: int):
    chat_type = request.POST.get("chat_type")
    selected_label = request.POST.get("selected_label")
    bento_name = request.POST.get("bento_name")

    # Extract metadata from form
    metadata = {}
    metadata_keys = request.POST.getlist("metadata_key[]")
    metadata_values = request.POST.getlist("metadata_value[]")

    # Combine keys and values into metadata dict, excluding empty entries
    for key, value in zip(metadata_keys, metadata_values):
        if key.strip() and value.strip():  # Only add non-empty key-value pairs
            metadata[key.strip()] = value.strip()

    chat = await Chat.objects.select_related("chatsetting").aget(id=chat_id)
    chat.chatsetting.chat_type = chat_type
    chat.chatsetting.selected_label = selected_label
    chat.chatsetting.bento_name = bento_name
    chat.chatsetting.metadata = metadata
    await chat.chatsetting.asave()
    return redirect("dashboard:chat_session", chat_id=chat_id)



@login_required
async def chat_send(request: HttpRequest, chat_id: int):
    message = request.POST.get("message")
    # Fetch chat and chatsetting in one query using select_related
    plugin_widgets = []
    plugins = settings.KITCHENAI.get("plugins", [])
    if plugins:
        #get the plugin objects from app configs 
        plugin_objects = [apps.get_app_config(plugin["name"]) for plugin in plugins]
        for plugin in plugin_objects:
            plugin_widgets.append(plugin.plugin.get_chat_metric_widget())


    chat = await Chat.objects.select_related('chatsetting').aget(id=chat_id)
    
    try:
        result = await query_handler(
            chat.chatsetting.selected_label, 
            QuerySchema(
                query=message, 
                stream=False, 
                metadata=chat.chatsetting.metadata
            )
        )
    except QueryHandlerBadRequestError as e:
        return TemplateResponse(
            request, 
            "dashboard/htmx/chat_response.html", 
            {"message": message, "error": e.message}
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
    metadata = result.metadata or {}
    logger.info(f"input: {result.input}")
    logger.info(f"output: {result.output}")
    metric = ChatMetric(
        input_text=result.input,
        output_text=result.output,
        chat=chat,
        metadata=metadata,
        sources_used=sources
    )

    if result.token_counts:
        metric.embedding_tokens = result.token_counts.embedding_tokens
        metric.llm_prompt_tokens = result.token_counts.llm_prompt_tokens 
        metric.llm_completion_tokens = result.token_counts.llm_completion_tokens
        metric.total_llm_tokens = result.token_counts.total_llm_tokens

    await metric.asave()

    #check if the response is empty and if so, send a signal to whoever is handling the query
    if not sources:
        await query_signal.asend(QuerySignalSender.POST_DASHBOARD_QUERY, **result.model_dump(), source_id=metric.id, error=True)
    else:
        await query_signal.asend(QuerySignalSender.POST_DASHBOARD_QUERY, **result.model_dump(), source_id=metric.id)

    return TemplateResponse(
        request,
        "dashboard/htmx/chat_response.html",
        {"message": message, 
         "metrics": metric,
         "plugin_widgets": plugin_widgets
        },
    )
