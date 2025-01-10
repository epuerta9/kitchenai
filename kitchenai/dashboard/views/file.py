from django.http import HttpRequest
from django.template.response import TemplateResponse
from kitchenai.core.models import FileObject
from kitchenai.dashboard.forms import FileUploadForm
from django.shortcuts import redirect
from django.apps import apps
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required


@login_required
async def file(request: HttpRequest):
    if request.method == "POST":
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
            )
        return redirect("dashboard:file")

    # Get pagination parameters
    page = int(request.GET.get('page', 1))
    per_page = int(request.GET.get('per_page', 10))

    # Calculate offset and limit
    offset = (page - 1) * per_page

    form = FileUploadForm()
    core_app = apps.get_app_config("core")
    if not core_app.kitchenai_app:
        return TemplateResponse(request, "dashboard/pages/error/no_app.html", {})
    labels = core_app.kitchenai_app.to_dict()
    storage_handlers = labels.get("storage_handlers", [])
    
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
            "storage_handlers": storage_handlers,
            "current_page": page,
            "total_pages": total_pages,
            "per_page": per_page,
            "total_files": total_files,
        },
    )

@login_required
async def delete_file(request: HttpRequest, file_id: int):
    await FileObject.objects.filter(id=file_id).adelete()
    return HttpResponse("")

