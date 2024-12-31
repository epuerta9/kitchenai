from django.http import HttpRequest
from django.template.response import TemplateResponse
from django.conf import settings
import logging
from kitchenai.bento.models import Bento
from kitchenai.core.models import KitchenAIManagement
from kitchenai.core.models import FileObject, EmbedObject
from kitchenai.dashboard.forms import FileUploadForm
from django.shortcuts import redirect
from django.apps import apps
from django.http import HttpResponse
from ..models import Chat, ChatMetric, AggregatedChatMetric, ChatSetting
from kitchenai.core.exceptions import QueryHandlerBadRequestError
from kitchenai.contrib.kitchenai_sdk.schema import QuerySchema, QueryBaseResponseSchema
from kitchenai.core.api.query import query_handler
from .bento import *

logger = logging.getLogger(__name__)


async def home(request: HttpRequest):
    kitchenai_settings = settings.KITCHENAI
    bentos = kitchenai_settings.get("bento", [])
    apps = kitchenai_settings.get("apps", [])
    plugins = kitchenai_settings.get("plugins", [])

    selected_bento = await Bento.objects.afirst()

    mgmt = await KitchenAIManagement.objects.filter(
        name="kitchenai_management"
    ).afirst()

    total_files = await FileObject.objects.acount()
    total_embeddings = await EmbedObject.objects.acount()

    return TemplateResponse(
        request,
        "dashboard/pages/home.html",
        {
            "bento": bentos,
            "apps": apps,
            "plugins": plugins,
            "selected_bento": selected_bento,
            "module_type": mgmt.module_path,
            "total_files": total_files,
            "total_embeddings": total_embeddings,
        },
    )


async def file(request: HttpRequest):
    if request.method == "POST":
        file = request.FILES.get("file")
        ingest_label = request.POST.get("ingest_label")

        # Extract metadata from form
        metadata = {}
        metadata_keys = request.POST.getlist("metadata_key[]")
        metadata_values = request.POST.getlist("metadata_value[]")

        # Combine keys and values into metadata dict, excluding empty entries
        for key, value in zip(metadata_keys, metadata_values):
            if key.strip() and value.strip():  # Only add non-empty key-value pairs
                metadata[key.strip()] = value.strip()

        if file and ingest_label:
            await FileObject.objects.acreate(
                file=file,
                name=file.name,
                ingest_label=ingest_label,
                metadata=metadata,  # Add metadata to the file object
            )
        return redirect("dashboard:file")

    form = FileUploadForm()
    core_app = apps.get_app_config("core")
    labels = core_app.kitchenai_app.to_dict()
    storage_handlers = labels.get("storage_handlers", [])
    files = FileObject.objects.all().order_by("-created_at")

    return TemplateResponse(
        request,
        "dashboard/pages/file.html",
        {
            "files": files,
            "form": form,
            "storage_handlers": storage_handlers,
        },
    )


async def delete_file(request: HttpRequest, file_id: int):
    await FileObject.objects.filter(id=file_id).adelete()
    return HttpResponse("")


async def labels(request: HttpRequest):
    core_app = apps.get_app_config("core")
    if not core_app.kitchenai_app:
        logger.error("No kitchenai app in core app config")
        return TemplateResponse(
            request,
            "dashboard/pages/labels.html",
            {},
        )
    return TemplateResponse(
        request,
        "dashboard/pages/labels.html",
        {
            "labels": core_app.kitchenai_app.to_dict(),
        },
    )


async def embeddings(request: HttpRequest):
    if request.method == "POST":
        text = request.POST.get("text")
        ingest_label = request.POST.get("ingest_label")

        # Extract metadata from form
        metadata = {}
        metadata_keys = request.POST.getlist("metadata_key[]")
        metadata_values = request.POST.getlist("metadata_value[]")

        # Combine keys and values into metadata dict, excluding empty entries
        for key, value in zip(metadata_keys, metadata_values):
            if key.strip() and value.strip():
                metadata[key.strip()] = value.strip()

        if text and ingest_label:
            await EmbedObject.objects.acreate(
                text=text,
                ingest_label=ingest_label,
                metadata=metadata,
                status="processing",  # Initial status
            )
        return redirect("dashboard:embeddings")

    # Get all embeddings sorted by creation date
    embeddings = EmbedObject.objects.all().order_by("-created_at")

    # Get available storage handlers for the dropdown
    core_app = apps.get_app_config("core")
    labels = core_app.kitchenai_app.to_dict()
    embed_handlers = labels.get("embed_handlers", [])

    return TemplateResponse(
        request,
        "dashboard/pages/embeddings.html",
        {
            "embeddings": embeddings,
            "embed_handlers": embed_handlers,
        },
    )


async def delete_embedding(request: HttpRequest, embedding_id: int):
    await EmbedObject.objects.filter(id=embedding_id).adelete()
    return HttpResponse("")


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
        labels = apps.get_app_config("core").kitchenai_app.to_dict()
        if labels["query_handlers"]:
            await ChatSetting.objects.acreate(chat=chat, selected_label=labels["query_handlers"][0], bento_name=name, chat_type=ChatSetting.ChatType.QUERY)
        else:
           return TemplateResponse(request, "dashboard/pages/errors.html", {"error": "No query handlers found"})
        return redirect("dashboard:chat_session", chat_id=chat.id)

    chats = Chat.objects.all()
    return TemplateResponse(request, "dashboard/pages/chat.html", {"chats": chats})


async def chat_session(request: HttpRequest, chat_id: int):
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
        },
    )

async def chat_delete(request: HttpRequest, chat_id: int):
    await Chat.objects.filter(id=chat_id).adelete()
    return HttpResponse("")


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



async def chat_send(request: HttpRequest, chat_id: int):
    message = request.POST.get("message")
    # Fetch chat and chatsetting in one query using select_related
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
    
    metric = await ChatMetric.objects.acreate(
        input_text=result.input, 
        output_text=result.output, 
        chat=chat,
        metadata=result.metadata,
        sources_used=sources
    )

    return TemplateResponse(
        request,
        "dashboard/htmx/chat_response.html",
        {"message": message, "metrics": metric},
    )
