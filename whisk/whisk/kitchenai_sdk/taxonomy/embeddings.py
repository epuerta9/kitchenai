from ..base import KitchenAITask, KitchenAITaskHookMixin
from ..schema import DependencyType

class EmbedTask(KitchenAITask, KitchenAITaskHookMixin):
    def __init__(self, namespace: str, dependency_manager=None):
        super().__init__(namespace, dependency_manager)
        self.namespace = namespace

    def handler(self, label: str, *dependencies: DependencyType):
        """Decorator for registering embed tasks with dependencies."""
        def decorator(func):
            @self.with_dependencies(*dependencies)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return self.register_task(label, wrapper)
        return decorator

    def on_delete(self, label: str, *dependencies: DependencyType):
        """Decorator for registering embed delete hooks with dependencies."""
        def decorator(func):
            @self.with_dependencies(*dependencies)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return self.register_hook(label, "on_delete", wrapper)
        return decorator
