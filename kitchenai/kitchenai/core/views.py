from django.http import HttpRequest
from django.template.response import TemplateResponse


async def home(request: HttpRequest):
    return TemplateResponse(
        request,
        "pages/home.html",
    )
