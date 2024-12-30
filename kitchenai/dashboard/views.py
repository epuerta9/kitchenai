from django.http import HttpRequest
from django.template.response import TemplateResponse
from falco_toolbox.types import HttpRequest
from django.conf import settings
import logging
from kitchenai.bento.models import Bento
from kitchenai.core.models import KitchenAIManagement
from kitchenai.core.models import FileObject, EmbedObject
from kitchenai.dashboard.forms import FileUploadForm
from django.shortcuts import redirect
from django.apps import apps
from django.http import HttpResponse
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
                metadata=metadata  # Add metadata to the file object
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
                status="processing"  # Initial status
            )
        return redirect("dashboard:embeddings")

    # Get all embeddings sorted by creation date
    embeddings = EmbedObject.objects.all().order_by("-created_at")
    
    # Get available storage handlers for the dropdown
    core_app = apps.get_app_config("core")
    labels = core_app.kitchenai_app.to_dict()
    storage_handlers = labels.get("storage_handlers", [])

    return TemplateResponse(
        request,
        "dashboard/pages/embeddings.html",
        {
            "embeddings": embeddings,
            "storage_handlers": storage_handlers,
        },
    )


async def delete_embedding(request: HttpRequest, embedding_id: int):
    await EmbedObject.objects.filter(id=embedding_id).adelete()
    return HttpResponse("")
