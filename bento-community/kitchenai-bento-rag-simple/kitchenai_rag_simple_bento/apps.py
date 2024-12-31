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

# Configure basic logging to stdout
logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
# Write to a file for debugging
debug_log = open("/tmp/kitchen_debug.log", "a")

# from django.apps import AppConfig
class KitchenaiRagSimpleBentoConfig(BentoBaseConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "kitchenai_rag_simple_bento"

    def ready(self):
        debug_log.write("\n=== App Ready Called ===\n")
        debug_log.write(f"Process ID: {os.getpid()}\n")
        
        try:
            from .kitchen import get_app
            app = get_app()  # This will ensure handlers are loaded
            debug_log.write(f"Kitchen app handlers: {app.to_dict()}\n")
        except Exception as e:
            debug_log.write(f"Error in ready(): {str(e)}\n")
            import traceback
            traceback.print_exc(file=debug_log)
        
        debug_log.write("=== App Ready Complete ===\n")
        debug_log.flush()
        
        return super().ready()
    


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

