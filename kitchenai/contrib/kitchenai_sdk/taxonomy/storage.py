from ..base import KitchenAITask, KitchenAITaskHookMixin
from typing import Callable


class StorageTask(KitchenAITask, KitchenAITaskHookMixin):

    def __init__(self, namespace: str):
        super().__init__(namespace)
        self.namespace = namespace

    def handler(self, label: str):
        """Decorator for registering storage tasks."""
        def decorator(func):
            return self.register_task(label, func)
        return decorator


    def on_delete(self, label: str):
        """Register a storage delete hook."""   
        def decorator(func):
            return self.register_hook(label, "on_delete", func)
        return decorator
