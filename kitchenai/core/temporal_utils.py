from temporalio import activity
import sys
from importlib import import_module, reload


def get_agent(module_path: str):
    """Dynamically load agent class, allowing for hot reloading"""
    try:
        # Split module path and class name
        module_path, class_name = module_path.rsplit('.', 1)
        
        # Import or reload the module
        if module_path in sys.modules:
            activity.logger.info(f"Reloading module {module_path}")
            module = reload(sys.modules[module_path])
        else:
            activity.logger.info(f"Importing module {module_path}")
            module = import_module(module_path)
        
        # Get the class and create a fresh instance
        AgentClass = getattr(module, class_name)
        return AgentClass()
        
    except Exception as e:
        activity.logger.error(f"Failed to load agent {module_path}: {str(e)}")
        raise