from ..base import KitchenAITask
import functools
from ..schema import DependencyType



class QueryTask(KitchenAITask):
    def __init__(self, namespace: str, dependency_manager=None):
        super().__init__(namespace, dependency_manager)
        self.namespace = namespace

    def handler(self, label: str, *dependencies: DependencyType):
        """Decorator for registering query tasks with dependencies."""
        def decorator(func):
            @functools.wraps(func)
            @self.with_dependencies(*dependencies)
            async def wrapper(*args, **kwargs):
                return await func(*args, **kwargs)
            return self.register_task(label, wrapper)
        return decorator
