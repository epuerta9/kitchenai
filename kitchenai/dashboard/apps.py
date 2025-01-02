from django.apps import AppConfig


class DashboardConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "kitchenai.dashboard"

    def ready(self):
        import kitchenai.dashboard.signals
