from django.http import HttpRequest
from django.template.response import TemplateResponse
from kitchenai.core.models import EmbedObject
from django.shortcuts import redirect
from django.apps import apps
from django.http import HttpResponse
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.contrib.auth.decorators import login_required


@login_required
async def embeddings(request: HttpRequest):
    # Default pagination parameters
    page = request.GET.get('page', 1)
    try:
        page = int(page)
    except ValueError:
        page = 1
    
    per_page = 10  # Items per page

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

    # Get total count and all embeddings ordered by creation date
    total_embeddings = await EmbedObject.objects.acount()
    all_embeddings = EmbedObject.objects.all().order_by("-created_at")

    # Create a list from async queryset for pagination
    embeddings_list = [embedding async for embedding in all_embeddings]
    
    # Create paginator
    paginator = Paginator(embeddings_list, per_page)
    total_pages = paginator.num_pages

    try:
        current_page_embeddings = paginator.page(page)
    except (EmptyPage, InvalidPage):
        # If page is out of range, deliver last page
        page = paginator.num_pages
        current_page_embeddings = paginator.page(paginator.num_pages)

    # Get available storage handlers for the dropdown
    core_app = apps.get_app_config("core")
    if not core_app.kitchenai_app:
        return TemplateResponse(request, "dashboard/pages/errors.html", {"error": "No embeddings found"})
    labels = core_app.kitchenai_app.to_dict()
    embed_handlers = labels.get("embed_handlers", [])

    return TemplateResponse(
        request,
        "dashboard/pages/embeddings.html",
        {
            "embeddings": current_page_embeddings,
            "embed_handlers": embed_handlers,
            "current_page": page,
            "total_pages": total_pages,
            "per_page": per_page,
            "total_embeddings": total_embeddings,
        },
    )

@login_required
async def delete_embedding(request: HttpRequest, embedding_id: int):
    await EmbedObject.objects.filter(id=embedding_id).adelete()
    return HttpResponse("")