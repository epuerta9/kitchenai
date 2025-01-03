from django.urls import path
from django.conf import settings
import djp
from django.urls import include
import os
from typing import Literal
from django.core.exceptions import ImproperlyConfigured
from kitchenai.core.schema.rag import RAGConfigSchema
from pydantic import ValidationError
from kitchenai.core.schema.base import validate_bento_config
from kitchenai.core.types import EnvVars, ModelType, ModelName, VectorStore
from kitchenai_rag_simple_bento.__version__ import __version__

def get_available_env_vars():
    """
    Returns information about all available environment variables and their configurations.
    
    Returns:
        dict: A dictionary describing each environment variable, its purpose, default value, and allowed values
    """
    try:
        return RAGConfigSchema(
            llm_type=os.environ.get(EnvVars.MODEL_TYPE, ModelType.LITELLM),
            llm_name=os.environ.get(EnvVars.MODEL_NAME, ModelName.GPT4O),
            temperature=float(os.environ.get(EnvVars.TEMPERATURE, "0.7")),
            vector_store=os.environ.get(EnvVars.VECTOR_STORE, VectorStore.CHROMA),
            chunk_size=int(os.environ.get(EnvVars.CHUNK_SIZE, "1024"))
        )
    except Exception as e:
        raise ImproperlyConfigured(f"Invalid RAG configuration: {str(e)}")


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

    # Validate RAG settings
    rag_config = get_available_env_vars()
    
    # Use the validated config
    settings = rag_config.model_dump()
    config = {
        "name": "kitchenai_rag_simple_bento",
        "description": "a simple RAG starter that covers majority of cases",
        "namespace": "simple_rag",
        "home": "home",
        "version": __version__,
        "tags": ["rag-simple", "bento", "kitchenai_rag_simple_bento", "kitchenai-bento-rag-simple"],
    }

    try:
        validate_bento_config(config)
    except ValidationError as e:
        raise ImproperlyConfigured(f"Invalid bento configuration: {str(e)}") from e

    config["settings"] = settings
    current_settings["KITCHENAI"]["bento"].append(config)
    current_settings["KITCHENAI_RAG_SIMPLE_BENTO"] = settings
    


@djp.hookimpl
def middleware():
    # A list of middleware class strings to add to MIDDLEWARE:
    # Wrap strings in djp.Before("middleware_class_name") or
    # djp.After("middleware_class_name") to specify before or after
    return []

