from django.urls import path
from django.conf import settings
import djp

@djp.hookimpl
def installed_apps():
    return ["deepeval_plugin"]


@djp.hookimpl
def urlpatterns():
    # A list of URL patterns to add to urlpatterns:
    return []


@djp.hookimpl
def settings(current_settings):
    # Make changes to the Django settings.py globals here
    current_settings["KITCHENAI"]["bento"].append({
        "name": "deepeval_plugin",
        "description": "deepeval integration with kitchenai",
        "tags": ["deepeval", "bento", "deepeval_plugin", "kitchenai-plugin-deepeval"],
    })
    


@djp.hookimpl
def middleware():
    # A list of middleware class strings to add to MIDDLEWARE:
    # Wrap strings in djp.Before("middleware_class_name") or
    # djp.After("middleware_class_name") to specify before or after
    return []