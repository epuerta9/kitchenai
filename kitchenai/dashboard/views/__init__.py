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
from kitchenai.core.signals.query import QuerySignalSender, query_signal
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.contrib.auth.decorators import login_required


from .file import *
from .settings import *
from .embeddings import *
from .chat import *

logger = logging.getLogger(__name__)

@login_required
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
            "is_local": settings.KITCHENAI_LOCAL,
        },
    )


@login_required
async def labels(request: HttpRequest):
    core_app = apps.get_app_config("core")
    if not core_app.kitchenai_app:
        logger.error("No kitchenai app in core app config")
        return TemplateResponse(request, "dashboard/pages/errors.html", {"error": "No kitchenai app loaded"})
    return TemplateResponse(
        request,
        "dashboard/pages/labels.html",
        {
            "labels": core_app.kitchenai_app.to_dict(),
        },
    )


