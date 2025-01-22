from django.http import HttpRequest
from django.template.response import TemplateResponse
from django.conf import settings
import logging
from kitchenai.core.models import FileObject, EmbedObject

from django.apps import apps

from django.contrib.auth.decorators import login_required

from kitchenai.core.utils import get_bento_clients_by_user
from .file import *
from .settings import *
from .embeddings import *
from .chat import *
from .bento import *

logger = logging.getLogger(__name__)

Organization =  apps.get_model(settings.AUTH_ORGANIZATION_MODEL)
OrganizationMember = apps.get_model(settings.AUTH_ORGANIZATIONMEMBER_MODEL)

@login_required
async def home(request: HttpRequest):
    kitchenai_settings = settings.KITCHENAI

    # Get the organization through the OrganizationMember relationship
    user = await request.auser()

    oss_bento_clients = get_bento_clients_by_user(user)

    total_files = await FileObject.objects.acount()
    total_embeddings = await EmbedObject.objects.acount()


    return TemplateResponse(
        request,
        "dashboard/pages/home.html",
        {
            "bento_boxes": oss_bento_clients,
            "apps": kitchenai_settings.get("apps", []),
            "plugins": kitchenai_settings.get("plugins", []),
            "total_files": total_files,
            "total_embeddings": total_embeddings,
            "LICENSE": settings.KITCHENAI_LICENSE,
        },
    )


@login_required
async def labels(request: HttpRequest):
    kitchenai_settings = settings.KITCHENAI

    # Get the organization through the OrganizationMember relationship
    user = await request.auser()

    oss_bento_clients = get_bento_clients_by_user(user)
    return TemplateResponse(
        request,
        "dashboard/pages/labels.html",
        {
            "bento_clients": oss_bento_clients,
        },
    )


