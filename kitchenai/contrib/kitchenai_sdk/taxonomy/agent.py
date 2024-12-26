from kitchenai.contrib.kitchenai_sdk.base import KitchenAITask
import functools
import asyncio

class AgentTask(KitchenAITask):
    """
    This is a class for registering agent tasks.
    """
    def __init__(self, namespace: str):
        super().__init__(namespace)
        self.namespace = namespace

    def handler(self, label: str):
        """Decorator for registering agent tasks."""
        def decorator(func):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                if asyncio.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                else:
                    loop = asyncio.get_event_loop()
                    return await loop.run_in_executor(None, functools.partial(func, *args, **kwargs))
            return self.register_task(f"{self.namespace}.{label}", wrapper)
        return decorator

    def on_create(self, label: str):
        """Decorator for registering agent hooks."""
        def decorator(func):
            return self.register_hook(label, "on_create", func)
        return decorator

    def on_success(self, label: str):
        """Decorator for registering agent hooks."""
        def decorator(func):
            return self.register_hook(label, "on_success", func)
        return decorator
