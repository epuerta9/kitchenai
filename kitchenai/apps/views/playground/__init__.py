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
    "llama-index",
]

async def home(request: HttpRequest):
    # Get user first to determine if we need an anonymous session
    user = await request.auser()
    selected_bento_id = request.GET.get('bento')
    selected_bento = None

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

    client_id = await request.session.aget('client_id', None)

 
    # Only create anonymous session for non-authenticated users
    session = await request.session.aget('anonymous_id')
    if not session:
        request.session['anonymous_id'] = str(uuid.uuid4())
        await request.session.aset_expiry(60 * 60 * 24 * 30)  # 30 days


    user_id = f"Anonymous {request.session['anonymous_id']}"
    
    logger.info(f"{user_id} is accessing the playground")
    
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
    
    kitchenai_bento_boxes = BentoClient.objects.filter(client_id__in=playground_bento_ids).all()
    # kitchenai_bento_boxes = [
    #     {
    #         "name": "PDF Assistant",
    #         "client_id": "pdf_assistant_001",
    #         "client_description": "Specialized in handling PDF documents, extracting text, and answering questions about PDF content.",
    #         "version": "1.0.0"
    #     },
    #     {
    #         "name": "Code Helper",
    #         "client_id": "code_helper_002",
    #         "client_description": "Assists with code review, bug fixing, and providing coding best practices across multiple languages.",
    #         "version": "1.2.1"
    #     },
    #     {
    #         "name": "Data Analyzer",
    #         "client_id": "data_analyzer_003",
    #         "client_description": "Processes and analyzes data files, generates insights, and creates visualizations.",
    #         "version": "0.9.5"
    #     },
    #     {
    #         "name": "Document Writer",
    #         "client_id": "doc_writer_004",
    #         "client_description": "Helps draft, edit, and format various types of documents including reports and articles.",
    #         "version": "1.1.0"
    #     },
    #     {
    #         "name": "Research Assistant",
    #         "client_id": "research_assist_005",
    #         "client_description": "Aids in research tasks, literature review, and summarizing academic papers.",
    #         "version": "0.8.2"
    #     }
    # ]
    if selected_bento_id in playground_bento_ids or selected_bento_id == client_id:
        selected_bento = await BentoClient.objects.filter(
            client_id=selected_bento_id,
            ack=True
        ).afirst()
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
