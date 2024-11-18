from django.apps import AppConfig
import posthog

class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "kitchenai.core"
    kitchenai_app = None

    def ready(self):
        posthog.api_key = 'phc_9X7VLQwkV5h90fb6DK85rk5uesGarhFfdf7vWc7AEQG'
        posthog.host = 'https://us.i.posthog.com'
