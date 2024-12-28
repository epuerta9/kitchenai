from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.views.decorators.http import require_http_methods
from falco_toolbox.htmx import for_htmx
from falco_toolbox.pagination import paginate_queryset
from falco_toolbox.types import HttpRequest


async def home(request: HttpRequest):
    return TemplateResponse(
        request,
        "pages/home.html",
    )

