from django.http import HttpRequest
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required

from falco_toolbox.htmx import for_htmx
from falco_toolbox.pagination import paginate_queryset


async def home(request: HttpRequest):
    return TemplateResponse(
        request,
        "pages/home.html",
    )
