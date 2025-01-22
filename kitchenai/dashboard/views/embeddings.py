from django.http import HttpRequest
from django.template.response import TemplateResponse
from kitchenai.core.models import EmbedObject
from django.shortcuts import redirect
from django.apps import apps
from django.http import HttpResponse
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.contrib.auth.decorators import login_required
from kitchenai.core.utils import get_bento_clients_by_user
from django.conf import settings
from django.urls import reverse


@login_required
async def embeddings(request: HttpRequest):
    BentoManager = apps.get_model(settings.KITCHENAI_BENTO_CLIENT_MODEL)
    client_id = request.GET.get("client_id", None)

    if request.method == "POST":
        bento_box_id = request.POST.get("bento_box_id")
        bento_box = await BentoManager.objects.aget(id=bento_box_id)
        text = request.POST.get("text")
        ingest_label = request.POST.get("ingest_label")

        # Extract metadata from form
        metadata = {}
        metadata_keys = request.POST.getlist("metadata_key[]")
        metadata_values = request.POST.getlist("metadata_value[]")

        for key, value in zip(metadata_keys, metadata_values):
            if key.strip() and value.strip():
                metadata[key.strip()] = value.strip()

        if text and ingest_label:
            await EmbedObject.objects.acreate(
                text=text,
                ingest_label=ingest_label,
                metadata=metadata,
                status="processing",
                bento_box=bento_box,
            )
            # Redirect with client_id query parameter
            redirect_url = f"{reverse('dashboard:embeddings')}?client_id={bento_box.client_id}"
            return redirect(redirect_url)

    # Get pagination parameters
    page = int(request.GET.get('page', 1))
    per_page = int(request.GET.get('per_page', 10))

    # Calculate offset and limit
    offset = (page - 1) * per_page

    user = await request.auser()
    bento_clients = get_bento_clients_by_user(user)

    if client_id:
        bento_box = await BentoManager.objects.filter(client_id=client_id).afirst()
    else:
        bento_box = None

    # Get total count for pagination
    total_embeddings = await EmbedObject.objects.acount()
    total_pages = (total_embeddings + per_page - 1) // per_page

    # Get paginated embeddings
    embeddings = EmbedObject.objects.all().order_by("-created_at")[offset:offset + per_page]

    return TemplateResponse(
        request,
        "dashboard/pages/embeddings.html",
        {
            "embeddings": embeddings,
            "bento_box": bento_box,
            "bento_clients": bento_clients,
            "client_id": client_id,
            "page": page,
            "total_pages": total_pages,
            "per_page": per_page,
            "total_embeddings": total_embeddings,
        },
    )

@login_required
async def delete_embedding(request: HttpRequest, embedding_id: int):
    embed = await EmbedObject.objects.select_related('bento_box').filter(id=embedding_id).afirst()
    if embed:
        await embed.adelete()
    return HttpResponse("")

