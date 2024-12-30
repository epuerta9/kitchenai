from django.http import HttpRequest
from django.template.response import TemplateResponse
from falco_toolbox.types import HttpRequest
from django.conf import settings
import logging
from kitchenai.bento.models import Bento
from kitchenai.core.models import KitchenAIManagement
from kitchenai.core.models import FileObject, EmbedObject

logger = logging.getLogger(__name__)


async def home(request: HttpRequest):
    kitchenai_settings = settings.KITCHENAI
    bentos = kitchenai_settings.get("bento", [])
    apps = kitchenai_settings.get("apps", [])
    plugins = kitchenai_settings.get("plugins", [])

    selected_bento = await Bento.objects.afirst()

    mgmt = await KitchenAIManagement.objects.filter(name="kitchenai_management").afirst()

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

