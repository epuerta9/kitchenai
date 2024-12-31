from kitchenai.bento.bento_config import BentoBaseConfig
from kitchenai.bento.types import DependencyType
from kitchenai.bento.manager import DependencyManager  
from typing import Any
from kitchenai.core.types import EnvVars
import logging
logger = logging.getLogger(__name__)
import logging
import sys
from django.apps import AppConfig
import os



class KitchenaiRagSimpleBentoConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "kitchenai_rag_simple_bento"

    def ready(self):
        import kitchenai_rag_simple_bento.query.query
        import kitchenai_rag_simple_bento.storage.vector
        import kitchenai_rag_simple_bento.embeddings.embeddings
        print("KitchenaiRagSimpleBentoConfig ready", file=sys.stdout)   


# class KitchenaiRagSimpleBentoConfig(BentoBaseConfig):
#     default_auto_field = "django.db.models.BigAutoField"
#     name = "kitchenai_rag_simple_bento"

#     def __init__(self, app_name, app_module):
#         print(f"RAGBento.__init__ for {app_name}", file=sys.stdout)
#         sys.stdout.flush()
        
#         # Inject the dependency manager implementation
#         dependency_manager = DependencyManager.get_instance(app_name)
#         super().__init__(app_name, app_module, dependency_manager)

#     def ready(self):
#         print(f"RAGBento.ready START for {self.name}", file=sys.stdout)
#         sys.stdout.flush()
        
#         # Debug: Print final app state
#         print("Apps in ready:", [app.name for app in apps.get_app_configs()], file=sys.stdout)
#         sys.stdout.flush()
        
#         return super().ready()

