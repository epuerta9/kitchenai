from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "kitchenai.core"
    kitchenai_app = None

    def ready(self):
        import kitchenai.core.signals
