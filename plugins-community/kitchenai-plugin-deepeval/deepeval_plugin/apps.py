from django.apps import AppConfig


class DeepevalPluginConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "deepeval_plugin"

    def ready(self):
        """Initialize KitchenAI app when Django starts"""
        from kitchenai.core.signals.query import query_signal, QuerySignalSender
        from .signals import answer_relevance_post_save, hallucination_post_save
        from .plugin import DeepEvalPlugin

        self.plugin = DeepEvalPlugin(query_signal, QuerySignalSender.POST_DASHBOARD_QUERY, self.name)

