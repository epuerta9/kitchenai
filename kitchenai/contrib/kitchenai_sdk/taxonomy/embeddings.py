
from ..base import KitchenAITask

class EmbedTask(KitchenAITask):
    def embed(self, label: str):
        """Decorator for registering embed tasks."""
        def decorator(func):
            return self.register_task(label, func)
        return decorator
