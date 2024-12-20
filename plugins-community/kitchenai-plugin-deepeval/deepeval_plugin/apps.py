from django.apps import AppConfig


class DeepevalPluginConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "deepeval_plugin"

    def ready(self):
        """Initialize KitchenAI app when Django starts"""
        pass