from django.urls import path
from django.conf import settings
import djp
from django.urls import include

@djp.hookimpl
def installed_apps():
    return ["kitchenai_playground_app"]


@djp.hookimpl
def urlpatterns():
    # A list of URL patterns to add to urlpatterns:
    return [
        path("playground/", include("kitchenai_playground_app.urls", namespace="playground")),

    ]


@djp.hookimpl
def settings(current_settings):
    # Make changes to the Django settings.py globals here
    current_settings["KITCHENAI"]["apps"].append({
        "name": "kitchenai_playground_app",
        "description": "app to interact with kitchenai backends",
        "namespace": "playground",
        "home": "home",
        "tags": ["kitchenai-playground", "app", "kitchenai_playground_app", "kitchenai-app-kitchenai-playground"],
    })
    


@djp.hookimpl
def middleware():
    # A list of middleware class strings to add to MIDDLEWARE:
    # Wrap strings in djp.Before("middleware_class_name") or
    # djp.After("middleware_class_name") to specify before or after
    return []