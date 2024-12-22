from kitchenai.contrib.kitchenai_sdk.base import KitchenAITask
import functools

class QueryTask(KitchenAITask):
    def query(self, label: str):
        """Decorator for registering query tasks."""
        def decorator(func):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                return await func(*args, **kwargs)
            return self.register_task(label, wrapper)
        return decorator
