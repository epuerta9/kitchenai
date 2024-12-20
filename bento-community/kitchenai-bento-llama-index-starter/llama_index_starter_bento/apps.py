from django.apps import AppConfig


class LlamaIndexStarterBentoConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "llama_index_starter_bento"

    def ready(self):
        """Initialize KitchenAI app when Django starts"""
        
        import llama_index_starter_bento.storage.vector
        import llama_index_starter_bento.query.query
        import llama_index_starter_bento.embeddings.embeddings
        
