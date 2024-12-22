from ..base import KitchenAITask
from typing import Callable


class StorageTask(KitchenAITask):
    def storage(self, label: str):
        """Decorator for registering storage tasks."""
        def decorator(func):
            return self.register_task(label, func)
        return decorator

    def storage_create_hook(self, label: str, hook: Callable):
        """Register a storage create hook."""
        self._tasks[f"{self.namespace}.{label}_hook"] = hook
