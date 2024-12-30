from django.urls import path
from django.conf import settings
import djp
from django.urls import include
import os
from typing import Literal
from django.core.exceptions import ImproperlyConfigured

# Define allowed values as constants
ALLOWED_MODEL_TYPES = ["litellm", "ollama"]
ALLOWED_MODEL_NAMES = {
    "litellm": ["gpt-4o", "gpt-4o-mini"],
    "ollama": ["llama2", "mistral", "mixtral"]
}

def get_available_env_vars():
    """
    Returns information about all available environment variables and their configurations.
    
    Returns:
        dict: A dictionary describing each environment variable, its purpose, default value, and allowed values
    """
    return {
        "KITCHENAI_SIMPLE_RAG_MODEL_TYPE": {
            "description": "The type of model to use",
            "default": "litellm",
            "allowed_values": ALLOWED_MODEL_TYPES,
            "required": False
        },
        "KITCHENAI_SIMPLE_RAG_MODEL_NAME": {
            "description": "The specific model to use",
            "default": "gpt-4o",
            "allowed_values": ALLOWED_MODEL_NAMES,
            "required": False,
            "note": "Allowed values depend on MODEL_TYPE selection"
        },
        "KITCHENAI_SIMPLE_RAG_TEMPERATURE": {
            "description": "Temperature for model responses (0.0 to 1.0)",
            "default": "0.7",
            "type": "float",
            "required": False
        },
        "KITCHENAI_SIMPLE_RAG_VECTOR_STORE": {
            "description": "Vector store backend to use",
            "default": "chroma",
            "required": False
        },
        "KITCHENAI_SIMPLE_RAG_CHUNK_SIZE": {
            "description": "Size of text chunks for processing",
            "default": "1024",
            "type": "integer",
            "required": False
        }
    }

@djp.hookimpl
def installed_apps():
    return ["kitchenai_rag_simple_bento"]


@djp.hookimpl
def urlpatterns():
    # A list of URL patterns to add to urlpatterns:
    return [
        path("simple-rag/", include("kitchenai_rag_simple_bento.urls", namespace="simple_rag")),
    ]

@djp.hookimpl
def settings(current_settings):
    # Make changes to the Django settings.py globals here

    model_type = os.environ.get("KITCHENAI_SIMPLE_RAG_MODEL_TYPE", "litellm")
    model_name = os.environ.get("KITCHENAI_SIMPLE_RAG_MODEL_NAME", "gpt-4o")

    # Validate model_type
    if model_type not in ALLOWED_MODEL_TYPES:
        raise ImproperlyConfigured(
            f"KITCHENAI_SIMPLE_RAG_MODEL_TYPE must be one of {ALLOWED_MODEL_TYPES}"
        )

    # Validate model_name based on model_type
    if model_name not in ALLOWED_MODEL_NAMES[model_type]:
        raise ImproperlyConfigured(
            f"For model_type '{model_type}', model_name must be one of {ALLOWED_MODEL_NAMES[model_type]}"
        )

    settings = {
        "model_type": model_type,
        "model_name": model_name,
        "temperature": float(os.environ.get("KITCHENAI_SIMPLE_RAG_TEMPERATURE", "0.7")),
        "vector_store": os.environ.get("KITCHENAI_SIMPLE_RAG_VECTOR_STORE", "chroma"),
        "chunk_size": int(os.environ.get("KITCHENAI_SIMPLE_RAG_CHUNK_SIZE", "1024")),
    }
    config = {
        "name": "kitchenai_rag_simple_bento",
        "description": "a simple RAG starter that covers majority of cases",
        "namespace": "simple_rag",
        "home": "home",
        "tags": ["rag-simple", "bento", "kitchenai_rag_simple_bento", "kitchenai-bento-rag-simple"],
    }

    config["settings"] = settings
    current_settings["KITCHENAI"]["bento"].append(config)
    current_settings["KITCHENAI_RAG_SIMPLE_BENTO"] = settings
    


@djp.hookimpl
def middleware():
    # A list of middleware class strings to add to MIDDLEWARE:
    # Wrap strings in djp.Before("middleware_class_name") or
    # djp.After("middleware_class_name") to specify before or after
    return []