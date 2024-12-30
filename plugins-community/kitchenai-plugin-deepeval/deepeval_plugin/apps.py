from django.apps import AppConfig


class DeepevalPluginConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "deepeval_plugin"

    def ready(self):
        """Initialize KitchenAI app when Django starts"""
        # from kitchenai.plugins.signals.evaluator import response_execute

        # from .plugin import EvaluatorPlugin

        # prompt_management = EvaluatorPlugin(response_execute, self.name)

        # prompt_management.on_load()
        pass