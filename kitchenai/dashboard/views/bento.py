from django.template.response import TemplateResponse
from falco_toolbox.types import HttpRequest
import aiohttp
import json
from django.conf import settings
import logging
from django.contrib.auth.decorators import login_required
logger = logging.getLogger(__name__)

@login_required
async def bento_install(request: HttpRequest):
    API_BASE_URL = "https://raw.githubusercontent.com/epuerta9/kitchenai/main"
    kitchenai_settings = settings.KITCHENAI
    bentos = kitchenai_settings.get("bento", [])

    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_BASE_URL}/bentos.json") as response:
            if response.status != 200:
                bento_boxes = []
            else:
                # Read as text and then parse JSON manually
                text = await response.text()
                try:
                    data = json.loads(text)
                    bento_boxes = data.get("bentos", [])
                except json.JSONDecodeError:
                    bento_boxes = []

    # Get set of installed bento names
    installed_bento_names = {bento["name"] for bento in bentos}
    logger.info(f"Installed bento names: {bento_boxes}")
    # Mark bentos as installed/not installed and ensure uniqueness
    unique_bentos = {}
    for bento in bento_boxes:
        name = bento["name"]
        if name not in unique_bentos:
            bento["installed"] = name in installed_bento_names
            unique_bentos[name] = bento
    
    # Convert back to list
    bento_boxes = list(unique_bentos.values())

    return TemplateResponse(request, "dashboard/pages/bento/install.html", {"bento_boxes": bento_boxes})