from collections.abc import Callable
import logging
from functools import wraps
import asyncio
from .schema import DependencyType
logger = logging.getLogger(__name__)

class KitchenAITask:
    def __init__(self, namespace: str, dependency_manager=None):
        self.namespace = namespace
        self._manager = dependency_manager
        self._tasks = {}
        self._hooks = {}    

    def with_dependencies(self, *dep_types: DependencyType) -> Callable:
        """Decorator to inject dependencies into task functions."""
        def decorator(func: Callable) -> Callable:
            # If no dependencies specified, return the original function
            if not dep_types:
                return func

            def get_dependencies():
                return [self._manager.get_dependency(dep_type) for dep_type in dep_types]

            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                deps = get_dependencies()
                return await func(*args, *deps, **kwargs)

            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                deps = get_dependencies()
                return func(*args, *deps, **kwargs)

            wrapper = async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
            return wrapper

        return decorator

    def register_task(self, label: str, func: Callable) -> Callable:
        task_key = f"{label}"
        self._tasks[task_key] = func
        return func

    def get_task(self, label: str) -> Callable | None:
        logger.info(f"Getting task for {label}")
        task_key = f"{label}"
        logger.info(f"Task key: {task_key}")
        return self._tasks.get(task_key)
    
    def list_tasks(self) -> dict:
        return list(self._tasks.keys())


class KitchenAITaskHookMixin:
    def register_hook(self, label: str, hook_type: str, func: Callable):
        """Register a hook function with the given label."""
        hook_key = f"{self.namespace}.{label}.{hook_type}"
        self._hooks[hook_key] = func
        return func

    def get_hook(self, label: str, hook_type: str) -> Callable | None:
        """Get a registered hook function by label."""
        hook_key = f"{self.namespace}.{label}.{hook_type}"
        return self._hooks.get(hook_key)

    def list_hooks(self) -> list:
        """List all registered hook labels."""
        return list(self._hooks.keys())