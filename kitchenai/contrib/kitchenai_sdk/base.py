from collections.abc import Callable
import functools
import importlib
import logging

logger = logging.getLogger(__name__)

class KitchenAITask:
    def __init__(self, namespace: str):
        self.namespace = namespace
        self._tasks = {}
        self._hooks = {}    


    def register_task(self, label: str, func: Callable):
        task_key = f"{self.namespace}.{label}"
        self._tasks[task_key] = func
        return func

    def get_task(self, label: str) -> Callable | None:
        logger.info(f"Getting task for {label}")
        task_key = f"{self.namespace}.{label}"
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