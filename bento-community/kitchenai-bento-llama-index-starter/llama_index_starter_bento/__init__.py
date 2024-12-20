from django.urls import path
from django.conf import settings
import djp

@djp.hookimpl
def installed_apps():
    return ["llama_index_starter_bento"]


@djp.hookimpl
def urlpatterns():
    # A list of URL patterns to add to urlpatterns:
    return []


@djp.hookimpl
def settings(current_settings):
    # Make changes to the Django settings.py globals here
    current_settings["KITCHENAI"]["bento"].append({
        "name": "llama_index_starter_bento",
        "description": "A llama index based bento box with essential RAG and AI functionalities",
        "tags": ["llama-index-starter", "bento", "llama_index_starter_bento", "kitchenai-bento-llama-index-starter"],
    })
    


@djp.hookimpl
def middleware():
    # A list of middleware class strings to add to MIDDLEWARE:
    # Wrap strings in djp.Before("middleware_class_name") or
    # djp.After("middleware_class_name") to specify before or after
    return []