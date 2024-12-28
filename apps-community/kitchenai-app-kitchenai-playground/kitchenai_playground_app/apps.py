from django.apps import AppConfig


class KitchenaiPlaygroundAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "kitchenai_playground_app"

    def ready(self):
        """Initialize KitchenAI app when Django starts"""
        from kitchenai.api import api
        from .router import router

        api.add_router("/playground/v1", router)
