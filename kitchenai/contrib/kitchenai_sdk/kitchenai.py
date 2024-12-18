import asyncio
import functools
import importlib
import logging
from collections.abc import Callable
from django.http import StreamingHttpResponse
from ninja import Router


from kitchenai.broker import broker

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class KitchenAIApp:
    def __init__(self, router: Router = None, namespace: str = 'default', default_db: str = "chromadb"):
        """
        A class that allows you to register routes and storage tasks for a given namespace
        """
        self._namespace = namespace
        self._router = router if router else Router()
        self._storage_tasks = {}
        self._storage_delete_tasks = {}
        self._storage_create_hooks = {}
        self._storage_delete_hooks = {}
        self._default_hook = "kitchenai.contrib.kitchenai_sdk.hooks.default_hook"
        self._default_db =  default_db
        self._query_handlers = {}
        self._query_stream_handlers = {}
        self._agent_handlers = {}
        self._embed_tasks= {}
        self._embed_delete_tasks = {}

    # Decorators for different route types
    def query(self, label: str,  **route_kwargs):
        """Query is a decorator for query handlers with the ability to add middleware"""
        def decorator(func, **route_kwargs):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                if asyncio.iscoroutinefunction(func):
                    result =  await func(*args, **kwargs)
                else:
                    loop = asyncio.get_event_loop()
                    result = await loop.run_in_executor(None, lambda: func(*args, **kwargs))
                return result
            self._query_handlers[f"{self._namespace}.{label}"] = wrapper
            return wrapper

        return decorator
    

    def embed(self, label: str, **route_kwargs):
        """Embed is a decorator for embed handlers"""
        def decorator(func):
            # Store the function immediately when the decorator is applied
            func_path = f"{func.__module__}.{func.__name__}"
            self._embed_tasks[f"{self._namespace}.{label}"] = func_path
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)  # Just execute the function normally
            return wrapper
        return decorator

    def storage(self, label: str, storage_create_hook: str = None):
        """Storage stores the functions in a hashmap and will run them as async tasks based on ingest_label"""
        def decorator(func):
            # Store the function immediately when the decorator is applied
            func_path = f"{func.__module__}.{func.__name__}"
            self._storage_tasks[f"{self._namespace}.{label}"] = func_path
            if storage_create_hook:
                self._storage_create_hooks[f"{self._namespace}.{label}"] = storage_create_hook
            elif self._storage_create_hooks.get(f"{self._namespace}.{label}") != self._default_hook and self._storage_create_hooks.get(f"{self._namespace}.{label}", None):
                pass
            else:
                logger.debug(f"Setting default success hook for {label}")
                self._storage_create_hooks[f"{self._namespace}.{label}"] = self._default_hook

            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)  # Just execute the function normally
            return wrapper
        return decorator

    def storage_delete(self, label: str):
        """Storage stores the functions in a hashmap and will run them as async tasks based on ingest_label"""
        def decorator(func):
            func_path = f"{func.__module__}.{func.__name__}"
            self._storage_delete_tasks[f"{self._namespace}.{label}"] = func_path
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)  # Just execute the function normally
            return wrapper
        return decorator
    
    def embed_delete(self, label: str):
        """Embed delete stores the functions in a hashmap and will run them as async tasks based on ingest_label"""
        def decorator(func):
            func_path = f"{func.__module__}.{func.__name__}"
            self._embed_delete_tasks[f"{self._namespace}.{label}"] = func_path
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)  # Just execute the function normally
            return wrapper
        return decorator

    def agent(self, label: str, **route_kwargs):
        """Agent is a decorator for agent handlers with the ability to add middleware"""
        def decorator(func, **route_kwargs):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                if asyncio.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                else:
                    loop = asyncio.get_event_loop()
                    return await loop.run_in_executor(None, lambda: func(*args, **kwargs))
            self._agent_handlers[f"{self._namespace}.{label}"] = wrapper

            return wrapper

        return decorator
    
    def stream(self, label: str, **route_kwargs):
        """Stream is a decorator for stream handlers. It returns a Generator function"""
        def decorator(func, **route_kwargs):

            self._query_stream_handlers[f"{self._namespace}.{label}"] = func

            return func

        return decorator

    def storage_create_hook(self, label: str):
        """Hooks are functions that are run after a storage task is successful"""
        def decorator(func):
            hook = f"{func.__module__}.{func.__name__}"

            self._storage_create_hooks[f"{self._namespace}.{label}"] = hook
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)  # Just execute the function normally
            return wrapper
        return decorator

    def storage_delete_hook(self, label: str):
        """Hooks are functions that are run after a storage task is successful"""
        def decorator(func):
            hook = f"{func.__module__}.{func.__name__}"

            self._storage_delete_hooks[f"{self._namespace}.{label}"] = hook
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)  # Just execute the function normally
            return wrapper
        return decorator

    def storage_tasks(self, label: str) -> Callable | None:
        """Returns the function associated with a given label"""
        func_path = self._storage_tasks.get(f"{self._namespace}.{label}")
        if func_path:
            module_path, func_name = func_path.rsplit(".", 1)
            module = importlib.import_module(module_path)
            return getattr(module, func_name)
        return None

    def storage_delete_tasks(self, label: str) -> Callable | None:
        """Returns the function associated with a given label"""
        func_path = self._storage_delete_tasks.get(f"{self._namespace}.{label}")
        if func_path:
            module_path, func_name = func_path.rsplit(".", 1)
            module = importlib.import_module(module_path)
            return getattr(module, func_name)
        return None

    def storage_tasks_list(self) -> dict:
        return self._storage_tasks

    def storage_create_hooks(self, label: str) -> Callable | None:
        """Returns the function associated with a given label"""
        func_path = self._storage_create_hooks.get(f"{self._namespace}.{label}")
        if func_path:
            module_path, func_name = func_path.rsplit(".", 1)
            module = importlib.import_module(module_path)
            return getattr(module, func_name)
        return None

    def storage_delete_hooks(self, label: str) -> Callable | None:
        """Returns the function associated with a given label"""
        func_path = self._storage_delete_hooks.get(f"{self._namespace}.{label}")
        if func_path:
            module_path, func_name = func_path.rsplit(".", 1)
            module = importlib.import_module(module_path)
            return getattr(module, func_name)
        return None

    def to_dict(self):
        return {
            "namespace": self._namespace,
            "query_handlers": list(self._query_handlers.keys()),
            "query_stream_handlers": list(self._query_stream_handlers.keys()),
            "agent_handlers": list(self._agent_handlers.keys()),
            "embed_tasks": list(self._embed_tasks.keys()),
            "embed_delete_tasks": list(self._embed_delete_tasks.keys()),
            "storage_tasks": list(self._storage_tasks.keys()),
            "storage_delete_tasks": list(self._storage_delete_tasks.keys()),
            "storage_create_hooks": list(self._storage_create_hooks.keys()),
            "storage_delete_hooks": list(self._storage_delete_hooks.keys()),
        }       