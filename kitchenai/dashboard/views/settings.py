from django.template.response import TemplateResponse
from django.contrib.auth.decorators import login_required
from django.conf import settings

@login_required
def settings_view(request):
    # Get KitchenAI settings
    kitchenai_settings = settings.KITCHENAI
    jwt_secret = settings.KITCHENAI_JWT_SECRET
    
    # Only show last 5 chars of JWT secret if it exists
    masked_jwt = f"...{jwt_secret[-5:]}" if jwt_secret else ""

    # Safely get storage settings
    storage_settings = settings.STORAGES.get('default', {})
    storage_options = storage_settings.get('OPTIONS', {})
    
    # Extract configurable environment variables
    env_settings = {
        "Core Settings": {
            "VERSION": settings.VERSION,
            "DEBUG": settings.DEBUG,
            "KITCHENAI_LOCAL": settings.KITCHENAI_LOCAL,
            "ALLOWED_HOSTS": settings.ALLOWED_HOSTS,
            "SECRET_KEY": "..." + settings.SECRET_KEY[-5:] if settings.SECRET_KEY else "",
            "TIME_ZONE": settings.TIME_ZONE,
        },
        "Email Settings": {
            "DEFAULT_FROM_EMAIL": settings.DEFAULT_FROM_EMAIL,
            "SERVER_EMAIL": settings.SERVER_EMAIL,
        },
        "Storage Settings": {
            "AWS_ACCESS_KEY_ID": "..." + storage_options.get("access_key", "")[-5:] if storage_options.get("access_key") else "",
            "AWS_STORAGE_BUCKET_NAME": storage_options.get("bucket_name"),
            "AWS_S3_REGION_NAME": storage_options.get("region_name"),
        },
        "KitchenAI Settings": {
            "KITCHENAI_AUTH": kitchenai_settings["settings"].get("auth", False),
            "KITCHENAI_THEME": settings.KITCHENAI_THEME,
            "KITCHENAI_JWT_SECRET": masked_jwt,
            "KITCHENAI_LLM_PROVIDER": settings.KITCHENAI_LLM_PROVIDER,
            "KITCHENAI_LLM_MODEL": settings.KITCHENAI_LLM_MODEL,
            "KITCHENAI_APP": settings.KITCHENAI_APP,
            "KITCHENAI_BENTO": settings.KITCHENAI.get("bento", []),
            "KITCHENAI_PLUGINS": settings.KITCHENAI.get("plugins", []),
            "KITCHENAI_APPS": settings.KITCHENAI.get("apps", []),
            "KITCHENAI_SETTINGS": settings.KITCHENAI.get("settings", {}),
            "KITCHENAI_SYSTEM_SETTINGS": {
                "is_answer_relevance_enabled": settings.KITCHENAI.get("settings", {}).get("is_answer_relevance_enabled", True),
                "is_faithfulness_enabled": settings.KITCHENAI.get("settings", {}).get("is_faithfulness_enabled", True),
                "is_contextual_relevancy_enabled": settings.KITCHENAI.get("settings", {}).get("is_contextual_relevancy_enabled", True),
                "is_hallucination_enabled": settings.KITCHENAI.get("settings", {}).get("is_hallucination_enabled", True),
                "is_toxicity_enabled": settings.KITCHENAI.get("settings", {}).get("is_toxicity_enabled", True),
            }
        },
        "Logging Settings": {
            "KITCHENAI_LOG_LEVEL": settings.LOGGING["loggers"]["kitchenai"]["level"],
        }
    }

    context = {
        "kitchenai_settings": {
            "bento": kitchenai_settings.get("bento", []),
            "plugins": kitchenai_settings.get("plugins", []),
            "apps": kitchenai_settings.get("apps", []),
            "settings": {
                "auth": kitchenai_settings["settings"].get("auth", False)
            },
            "jwt_secret": masked_jwt
        },
        "env_settings": env_settings
    }

    return TemplateResponse(
        request,
        "dashboard/pages/settings.html",
        context
    )