import sys
from django.apps import apps
from kitchenai.contrib.kitchenai_sdk.kitchenai import KitchenAIApp
from kitchenai.bento.manager import DependencyManager
import logging
import os

# Write to a file for debugging
debug_log = open("/tmp/kitchen_debug.log", "a")
debug_log.write("\n=== New Kitchen Module Load ===\n")
debug_log.flush()

# Create the app instance at module level
debug_log.write("Creating KitchenAI app\n")
dependency_manager = DependencyManager.get_instance("kitchenai_rag_simple_bento")
app = KitchenAIApp(namespace="kitchenai_rag_simple_bento", manager=dependency_manager)

def trigger_registration():
    """Force decorator execution by creating a temporary handler"""
    debug_log.write("Triggering registration\n")
    
    @app.query.handler("_temp")
    def _temp_handler():
        pass
    
    # Remove the temporary handler
    app.query._tasks.pop("_temp", None)
    
    debug_log.write(f"After trigger: {app.to_dict()}\n")
    debug_log.flush()

def get_app():
    """Get or create the app instance with handlers loaded"""
    global app
    
    if not any([app.query._tasks, app.storage._tasks, app.embeddings._tasks]):
        debug_log.write("Loading handlers\n")
        try:
            # Import the modules
            import kitchenai_rag_simple_bento.query.query
            import kitchenai_rag_simple_bento.storage.vector
            import kitchenai_rag_simple_bento.embeddings.embeddings
            
            # Trigger the decorators
            trigger_registration()
            
            debug_log.write(f"Final app state: {app.to_dict()}\n")
        except Exception as e:
            debug_log.write(f"Error loading handlers: {str(e)}\n")
            import traceback
            traceback.print_exc(file=debug_log)
    
    debug_log.write(f"Returning app with handlers: {app.to_dict()}\n")
    debug_log.flush()
    return app

# Trigger registration when module is loaded
trigger_registration()

# Export both the raw app and the getter
__all__ = ['app', 'get_app']
