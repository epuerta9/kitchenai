from django.http import HttpRequest
from django.template.response import TemplateResponse
from django.conf import settings
import logging
from django.apps import apps
import uuid
from django.http import HttpResponseRedirect
logger = logging.getLogger(__name__)

Organization = apps.get_model(settings.AUTH_ORGANIZATION_MODEL)
OrganizationMember = apps.get_model(settings.AUTH_ORGANIZATIONMEMBER_MODEL)
BentoClient = apps.get_model(settings.KITCHENAI_BENTO_CLIENT_MODEL)

from kitchenai.apps.views.playground.chat import *
from kitchenai.apps.views.playground.evaluations import *

playground_bento_ids = [
    6,
]

async def home(request: HttpRequest):
    """The home page for the playground. Allows anonymous users to connect and interact with our bento boxes"""
    
    # Get user first to determine if we need an anonymous session
    selected_bento_pk = request.GET.get('bento')

    #request for a client_id
    client_id = None
    if request.method == 'POST':
        client_id_request = request.POST.get('request_client_id')
        if client_id_request:
            #make a new client id. This is done via GET for simplicity. It will not remain in the URL. We'll store this in the session
            client_id = str(uuid.uuid4())
            await request.session.aset('client_id', client_id)
        
        return HttpResponseRedirect(request.path)

    await request.session.aset('allowed_bento_ids', playground_bento_ids)

    #the users bento client_id
    client_id = await request.session.aget('client_id', None)

 
    session = await request.session.aget('anonymous_id')
    if not session:
        request.session['anonymous_id'] = str(uuid.uuid4())
        await request.session.aset_expiry(60 * 60 * 24 * 30)  # 30 days

    
    if client_id:
        # Get users bento box by client id. We have already given the user a client_id and they are allowed to connect a bento box to it
        client_bento_box = (
            await BentoClient.objects.filter(client_id=client_id, ack=True)
            .order_by("-last_seen")
            .afirst()
        )
    else:
        client_bento_box = None

    #selectable bento boxes. We will show the user the available kitchenai bento boxes but with added descriptions 
    kitchenai_bento_boxes = BentoClient.objects.filter(pk__in=playground_bento_ids).all()

    # Find selected bento from existing objects
    selected_bento = None
    if selected_bento_pk:
        if client_bento_box and int(selected_bento_pk) == client_bento_box.id:
            selected_bento = client_bento_box
        else:
            # Look in kitchenai_bento_boxes
            async for bento in kitchenai_bento_boxes:
                if bento.id == int(selected_bento_pk):
                    selected_bento = bento
    
    logger.info(f"selected_bento_pk: {selected_bento_pk}")
    logger.info(f"client_bento_box: {client_bento_box}")


    logger.info(f"selected_bento: {selected_bento}")
    # Dummy code for display
    dummy_code = """from langchain import PyPDFLoader

def pdf_to_text(file_path):
    loader = PyPDFLoader(file_path)
    pages = loader.load()
    return ' '.join([page.page_content for page in pages])
"""
    chat_history = await request.session.aget('chat_history', [])

    return TemplateResponse(
        request,
        "apps/playground/pages/home.html",
        {
            "code": dummy_code,
            "messages": [],  # Empty list for chat messages
            "client_id": client_id,
            "client_bento_box": client_bento_box,
            "kitchenai_bento_boxes": kitchenai_bento_boxes,
            "selected_bento": selected_bento,
            "chat_history": chat_history,
        },
    )
