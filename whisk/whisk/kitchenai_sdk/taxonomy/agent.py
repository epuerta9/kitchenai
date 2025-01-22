from ..base import KitchenAITask
from ..schema import DependencyType
import functools
import asyncio

class AgentTask(KitchenAITask):
    """
    This is a class for registering agent tasks.
    """
    def __init__(self, namespace: str, dependency_manager=None):
        super().__init__(namespace, dependency_manager)
        self.namespace = namespace

    def handler(self, label: str, *dependencies: DependencyType):
        """Decorator for registering agent tasks with dependencies."""
        def decorator(func):
            @functools.wraps(func)
            @self.with_dependencies(*dependencies)
            async def wrapper(*args, **kwargs):
                if asyncio.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                else:
                    loop = asyncio.get_event_loop()
                    return await loop.run_in_executor(None, functools.partial(func, *args, **kwargs))
            return self.register_task(label, wrapper)
        return decorator

    def on_create(self, label: str, *dependencies: DependencyType):
        """Decorator for registering agent creation hooks with dependencies."""
        def decorator(func):
            @self.with_dependencies(*dependencies)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return self.register_hook(label, "on_create", wrapper)
        return decorator

    def on_success(self, label: str, *dependencies: DependencyType):
        """Decorator for registering agent success hooks with dependencies."""
        def decorator(func):
            @self.with_dependencies(*dependencies)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return self.register_hook(label, "on_success", wrapper)
        return decorator
