from django.http import HttpRequest
from django.template.response import TemplateResponse

from falco_toolbox.types import HttpRequest
from django.contrib.auth.decorators import login_required


@login_required
async def home(request: HttpRequest):
    return TemplateResponse(
        request,
        "pages/home.html",
    )

