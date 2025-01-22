from django.http import HttpRequest
from django.template.response import TemplateResponse
from kitchenai.core.models import FileObject
from kitchenai.dashboard.forms import FileUploadForm
from django.shortcuts import redirect
from django.apps import apps
from django.http import HttpResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required
import logging
logger = logging.getLogger(__name__)

@login_required
async def delete_bento(request: HttpRequest, bento_id: int):
    logger.info(f"Deleting bento {bento_id}")
    BentoClient = apps.get_model(settings.KITCHENAI_BENTO_CLIENT_MODEL)
    EmbedObject = apps.get_model('core', 'EmbedObject')
    FileObject = apps.get_model('core', 'FileObject')
    
    # # Delete embeds first, with pre-loaded bento_box relation
    # await EmbedObject.objects.select_related('bento_box').filter(bento_box_id=bento_id).adelete()
    
    # # Delete files
    # await FileObject.objects.select_related('bento_box').filter(bento_box_id=bento_id).adelete()
    
    # Delete the bento client
    await BentoClient.objects.filter(id=bento_id).adelete()
    
    return HttpResponse("")
