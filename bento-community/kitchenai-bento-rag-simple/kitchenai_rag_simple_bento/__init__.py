from django.urls import path
from django.conf import settings
import djp

@djp.hookimpl
def installed_apps():
    return ["kitchenai_rag_simple_bento"]


@djp.hookimpl
def urlpatterns():
    # A list of URL patterns to add to urlpatterns:
    return []


@djp.hookimpl
def settings(current_settings):
    # Make changes to the Django settings.py globals here
    current_settings["KITCHENAI"]["bento"].append({
        "name": "kitchenai_rag_simple_bento",
        "description": "a simple RAG starter that covers majority of cases",
        "tags": ["rag-simple", "bento", "kitchenai_rag_simple_bento", "kitchenai-bento-rag-simple"],
    })
    


@djp.hookimpl
def middleware():
    # A list of middleware class strings to add to MIDDLEWARE:
    # Wrap strings in djp.Before("middleware_class_name") or
    # djp.After("middleware_class_name") to specify before or after
    return []