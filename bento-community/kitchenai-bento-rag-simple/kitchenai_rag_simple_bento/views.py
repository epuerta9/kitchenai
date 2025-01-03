from django.template.response import TemplateResponse
from falco_toolbox.types import HttpRequest
from django.contrib.auth.decorators import login_required
import inspect
import json
from kitchenai_rag_simple_bento import get_available_env_vars


@login_required
async def home(request: HttpRequest):
    from django.conf import settings
    loaded_bentos = settings.KITCHENAI["bento"]
    loaded_bento = next((bento for bento in loaded_bentos if bento["name"] == "kitchenai_rag_simple_bento"), None)
    from .kitchen import app

    # Get tasks from each task type (query, storage, embeddings)
    handlers = {}

    # Query tasks
    query_tasks = app.query.list_tasks()
    for task in query_tasks:
        handler = app.query.get_task(task)
        if handler:
            handlers[f"{task}_handler"] = {
                'name': task.title().replace('_', ' ') + ' Handler',
                'code': inspect.getsource(handler),
                'docstring': handler.__doc__ or 'No documentation available'
            }
            
    # Storage tasks
    storage_tasks = app.storage.list_tasks()
    for task in storage_tasks:
        handler = app.storage.get_task(task)
        if handler:
            handlers[f"{task}_handler"] = {
                'name': task.title().replace('_', ' ') + ' Handler',
                'code': inspect.getsource(handler),
                'docstring': handler.__doc__ or 'No documentation available'
            }
            
    # Embeddings tasks
    embeddings_tasks = app.embeddings.list_tasks()
    for task in embeddings_tasks:
        handler = app.embeddings.get_task(task)
        if handler:
            handlers[f"{task}_handler"] = {
                'name': task.title().replace('_', ' ') + ' Handler',
                'code': inspect.getsource(handler),
                'docstring': handler.__doc__ or 'No documentation available'
            }
    
    
    return TemplateResponse(
        request,
        "kitchenai_rag_simple_bento/pages/home.html",
        {
            "config": loaded_bento,
            "handlers": handlers
        }
    )

@login_required
async def settings_view(request, bento_name):
    from django.conf import settings

    loaded_bentos =  settings.KITCHENAI["bento"]
    loaded_bento = next((bento for bento in loaded_bentos if bento["name"] == bento_name), None)
    settings = json.dumps(loaded_bento["settings"], indent=4)

    available_env_vars = get_available_env_vars().model_dump()

    return TemplateResponse(request, 'kitchenai_rag_simple_bento/pages/settings.html', {'settings': settings, 'config': loaded_bento, 'available_env_vars': available_env_vars})