from django.http import HttpRequest
from django.template.response import TemplateResponse
from django.conf import settings
import logging
from kitchenai.bento.models import Bento
from kitchenai.core.models import KitchenAIManagement
from kitchenai.core.models import FileObject, EmbedObject

from django.apps import apps

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

    org_member = request.org_data
    logger.info(f"Org member: {org_member}")

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
            "total_files": total_files,
            "total_embeddings": total_embeddings,
            "is_local": settings.KITCHENAI_LOCAL,
            "org_member": org_member,
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


