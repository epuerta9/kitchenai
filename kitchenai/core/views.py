from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.views.decorators.http import require_http_methods
from falco_toolbox.htmx import for_htmx
from falco_toolbox.pagination import paginate_queryset
from falco_toolbox.types import HttpRequest

from .forms import KitchenAIModuleForm
from .models import KitchenAIModule


async def home(request: HttpRequest):
    return TemplateResponse(
        request,
        "pages/home.html",
    )


@for_htmx(use_partial="table")
def kitchenaimodule_list(request: HttpRequest):
    kitchenaimodules = KitchenAIModule.objects.order_by("name")
    return TemplateResponse(
        request,
        "core/kitchenaimodule_list.html",
        context={"kitchenaimodules_page": paginate_queryset(request, kitchenaimodules)},
    )


def kitchenaimodule_detail(request: HttpRequest, pk: int):
    kitchenaimodule = get_object_or_404(KitchenAIModule.objects, pk=pk)
    return TemplateResponse(
        request,
        "core/kitchenaimodule_detail.html",
        context={"kitchenaimodule": kitchenaimodule},
    )


def kitchenaimodule_create(request: HttpRequest):
    form = KitchenAIModuleForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("core:kitchenaimodule_list")
    return TemplateResponse(
        request,
        "core/kitchenaimodule_create.html",
        context={"form": form},
    )


def kitchenaimodule_update(request: HttpRequest, pk: int):
    kitchenaimodule = get_object_or_404(KitchenAIModule.objects, pk=pk)
    form = KitchenAIModuleForm(
        request.POST or None, request.FILES or None, instance=kitchenaimodule
    )
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("core:kitchenaimodule_detail", pk=pk)
    return TemplateResponse(
        request,
        "core/kitchenaimodule_update.html",
        context={"kitchenaimodule": kitchenaimodule, "form": form},
    )


@require_http_methods(["DELETE"])
def kitchenaimodule_delete(_: HttpRequest, pk: int):
    KitchenAIModule.objects.filter(pk=pk).delete()
    return HttpResponse("")
