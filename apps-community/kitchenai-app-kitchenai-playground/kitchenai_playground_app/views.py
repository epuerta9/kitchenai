from django.shortcuts import render
from django.template.response import TemplateResponse
from django.views.decorators.http import require_http_methods
from falco_toolbox.htmx import for_htmx
from falco_toolbox.pagination import paginate_queryset
from falco_toolbox.types import HttpRequest


# Create your views here.


async def home(request: HttpRequest):
    return TemplateResponse(
        request,
        "kitchenai_playground_app/pages/home.html",
    )