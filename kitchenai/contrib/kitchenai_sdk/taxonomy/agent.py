from kitchenai.contrib.kitchenai_sdk.base import KitchenAITask
import functools
import asyncio

class AgentTask(KitchenAITask):
    def agent(self, label: str):
        """Decorator for registering agent tasks."""
        def decorator(func):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                if asyncio.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                else:
                    loop = asyncio.get_event_loop()
                    return await loop.run_in_executor(None, functools.partial(func, *args, **kwargs))
            return self.register_task(label, wrapper)
        return decorator
