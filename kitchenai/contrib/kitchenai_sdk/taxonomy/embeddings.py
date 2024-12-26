
from ..base import KitchenAITask, KitchenAITaskHookMixin

class EmbedTask(KitchenAITask, KitchenAITaskHookMixin):
    def __init__(self, namespace: str):
        super().__init__(namespace)
        self.namespace = namespace

    def handler(self, label: str):
        """Decorator for registering embed tasks."""
        def decorator(func):
            return self.register_task(label, func)
        return decorator

    def on_delete(self, label: str):
        """Decorator for registering embed tasks."""
        def decorator(func):
            return self.register_hook(label, "on_delete", func)
        return decorator
