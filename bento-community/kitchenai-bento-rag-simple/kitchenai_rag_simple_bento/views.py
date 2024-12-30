from django.shortcuts import render

# Create your views here.


from django.shortcuts import render
from django.template.response import TemplateResponse
from falco_toolbox.types import HttpRequest
from kitchenai_rag_simple_bento import get_available_env_vars
import json
# Create your views here.
async def home(request: HttpRequest):
    from django.conf import settings
    loaded_bentos =  settings.KITCHENAI["bento"]
    loaded_bento = next((bento for bento in loaded_bentos if bento["name"] == "kitchenai_rag_simple_bento"), None)
    
    return TemplateResponse(
        request,
        "kitchenai_rag_simple_bento/pages/home.html",
        {
            "config": loaded_bento,
        }
    )

async def settings_view(request, bento_name):
    from django.conf import settings

    loaded_bentos =  settings.KITCHENAI["bento"]
    loaded_bento = next((bento for bento in loaded_bentos if bento["name"] == bento_name), None)
    settings = json.dumps(loaded_bento["settings"], indent=4)

    available_env_vars = get_available_env_vars()

    return render(request, 'kitchenai_rag_simple_bento/pages/settings.html', {'settings': settings, 'config': loaded_bento, 'available_env_vars': available_env_vars})