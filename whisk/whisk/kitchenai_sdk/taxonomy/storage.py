from ..base import KitchenAITask, KitchenAITaskHookMixin
import functools
from ..schema import DependencyType

class StorageTask(KitchenAITask, KitchenAITaskHookMixin):
    """
    This is a class for registering storage tasks.
    """
    def __init__(self, namespace: str, dependency_manager=None):
        super().__init__(namespace, dependency_manager)
        self.namespace = namespace

    def handler(self, label: str, *dependencies: DependencyType):
        """Decorator for registering storage tasks with dependencies."""
        def decorator(func):
            @functools.wraps(func)
            @self.with_dependencies(*dependencies)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return self.register_task(label, wrapper)
        return decorator

    def on_store(self, label: str, *dependencies: DependencyType):
        """Decorator for registering storage hooks with dependencies."""
        def decorator(func):
            @self.with_dependencies(*dependencies)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return self.register_hook(label, "on_store", wrapper)
        return decorator
    
    def on_delete(self, label: str, *dependencies: DependencyType):
        """Decorator for registering deletion hooks with dependencies."""
        def decorator(func):
            @self.with_dependencies(*dependencies)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return self.register_hook(label, "on_delete", wrapper)
        return decorator

    def on_retrieve(self, label: str, *dependencies: DependencyType):
        """Decorator for registering retrieval hooks with dependencies."""
        def decorator(func):
            @self.with_dependencies(*dependencies)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return self.register_hook(label, "on_retrieve", wrapper)
        return decorator
