from django.http import HttpRequest
from django.template.response import TemplateResponse
from kitchenai.core.models import FileObject
from kitchenai.dashboard.forms import FileUploadForm
from django.shortcuts import redirect
from django.apps import apps
from django.http import HttpResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from kitchenai.core.utils import get_bento_clients_by_user
from django.urls import reverse

@login_required
async def file(request: HttpRequest):
    BentoManager = apps.get_model(settings.KITCHENAI_BENTO_CLIENT_MODEL)
    client_id = request.GET.get("client_id", None)
    if request.method == "POST":
        bento_box_id = request.POST.get("bento_box_id", None)
        bento_box = await BentoManager.objects.aget(id=bento_box_id)
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
                metadata=metadata,  # Add metadata to the file object
                bento_box=bento_box,
            )
        redirect_url = f"{reverse('dashboard:file')}?client_id={bento_box.client_id}"
        return redirect(redirect_url)

    # Get pagination parameters
    page = int(request.GET.get('page', 1))
    per_page = int(request.GET.get('per_page', 10))

    # Calculate offset and limit
    offset = (page - 1) * per_page

    form = FileUploadForm()
    user = await request.auser()
    bento_clients = get_bento_clients_by_user(user)

    if client_id:
        #user has a selected a bento box so lets use it
        bento_box = await BentoManager.objects.filter(client_id=client_id).afirst()
    else:
        #user has not selected a bento box so lets use the default
        bento_box = None
        
    # Get total count for pagination
    total_files = await FileObject.objects.acount()
    total_pages = (total_files + per_page - 1) // per_page

    # Get paginated files
    files = FileObject.objects.all().order_by("-created_at")[offset:offset + per_page].all()

    return TemplateResponse(
        request,
        "dashboard/pages/file.html",
        {
            "files": files,
            "form": form,
            "bento_box": bento_box,
            "current_page": page,
            "client_id": client_id,
            "bento_clients": bento_clients,
            "total_pages": total_pages,
            "per_page": per_page,
            "total_files": total_files,
        },
    )

@login_required
async def delete_file(request: HttpRequest, file_id: int):
    file = await FileObject.objects.select_related('bento_box').filter(id=file_id).afirst()
    if file:
        await file.adelete()
    return HttpResponse("")

