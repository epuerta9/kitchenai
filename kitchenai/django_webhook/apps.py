# pylint: disable=import-outside-toplevel

from django.apps import AppConfig


class WebhooksConfig(AppConfig):
    name = "kitchenai.django_webhook"
    default_auto_field = "django.db.models.AutoField"

    def ready(self):
        # pylint: disable=unused-import
        import kitchenai.django_webhook.checks
        from kitchenai.django_webhook.models import populate_topics_from_settings
        from kitchenai.django_webhook.signals import connect_signals

        connect_signals()
        populate_topics_from_settings()
