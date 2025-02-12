from collections.abc import Callable
import logging
from functools import wraps
import asyncio
from .schema import DependencyType
from typing import Any, Dict

logger = logging.getLogger(__name__)

class DependencyManager:
    """Manages dependencies for KitchenAI apps"""
    
    def __init__(self):
        self._dependencies: Dict[DependencyType, Any] = {}
        
    def register_dependency(self, dependency_type: DependencyType, dependency: Any):
        """Register a dependency"""
        self._dependencies[dependency_type] = dependency
        
    def get_dependency(self, dependency_type: DependencyType) -> Any:
        """Get a registered dependency"""
        if dependency_type not in self._dependencies:
            raise KeyError(f"Dependency {dependency_type} not registered")
        return self._dependencies[dependency_type]
    
    def has_dependency(self, dependency_type: DependencyType) -> bool:
        """Check if a dependency is registered"""
        return dependency_type in self._dependencies

class KitchenAITask:
    def __init__(self, namespace: str, manager=None):
        self.namespace = namespace
        self._manager = manager
        self._tasks = {}  # Task registry should be here in base class
        self._hooks = {}    

    def with_dependencies(self, *dep_types: DependencyType) -> Callable:
        """Decorator to inject dependencies into task functions."""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Inject requested dependencies into kwargs
                if self._manager:
                    for dep_type in dep_types:
                        if self._manager.has_dependency(dep_type):
                            kwargs[dep_type.value] = self._manager.get_dependency(dep_type)
                return await func(*args, **kwargs)
            return wrapper
        return decorator

    def register_task(self, label: str, task):
        """Register a task with a label"""
        self._tasks[label] = task
        return task

    def get_task(self, label: str):
        """Get a task by label"""
        return self._tasks.get(label)

    def list_tasks(self):
        """List all registered tasks"""
        return self._tasks


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