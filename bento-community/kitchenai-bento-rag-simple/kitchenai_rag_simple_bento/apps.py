from django.apps import AppConfig


class KitchenaiRagSimpleBentoConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "kitchenai_rag_simple_bento"

    def ready(self):
        """Initialize KitchenAI app when Django starts"""
        
        import kitchenai_rag_simple_bento.storage.vector
        import kitchenai_rag_simple_bento.query.query
        import kitchenai_rag_simple_bento.embeddings.embeddings
        
