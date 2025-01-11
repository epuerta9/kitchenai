

from django.apps import AppConfig

class KitchenaiRagSimpleBentoConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "kitchenai_rag_simple_bento"

    def ready(self):
        # Import kitchen to ensure app and handlers are initialized
        from .kitchen import app