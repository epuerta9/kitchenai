from ninja import Router
import functools
import logging
import asyncio
from django.http import StreamingHttpResponse
from typing import Optional, Callable
import importlib

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

    def _create_decorator(self, route_type: str, method: str, label: str, streaming=False):
        def decorator(func, **route_kwargs):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                if streaming:
                    #NOTE: Streaming HTTP response is only a synchronous operation
                    def event_generator():
                        for event in func(*args, **kwargs):
                            yield event

                    return StreamingHttpResponse(
                        func(*args, **kwargs),
                        content_type="text/event-stream",
                        headers={
                            'Cache-Control': 'no-cache',
                            'Transfer-Encoding': 'chunked',
                            'X-Accel-Buffering': 'no',
                        }
                    )
                # Non-streaming behavior
                elif asyncio.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                else:
                    loop = asyncio.get_event_loop()
                    return await loop.run_in_executor(None, lambda: func(*args, **kwargs))


            # Define the path for the route using the namespace and label
            route_path = f"/{route_type}/{label}"

            # Register the route using add_api_operation
            self._router.add_api_operation(
                path=route_path,
                methods=[method],
                view_func=wrapper,
                **route_kwargs
            )
            logger.debug(f"Registered route: {route_path} with streaming: {streaming}")
            return wrapper
        return decorator

    # Decorators for different route types
    def query(self, label: str, **route_kwargs):
        return self._create_decorator('query', "POST", label)

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

    def embedding(self, label: str, **route_kwargs):
        return self._create_decorator('embedding', "POST", label)

    def runnable(self, label: str, streaming=False, **route_kwargs):
        # Allows setting streaming=True to enable streaming responses
        return self._create_decorator('runnable', "POST", label, streaming=streaming)

    def agent(self, label: str, **route_kwargs):
        return self._create_decorator('agent', "POST", label)
    
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

    def storage_tasks(self, label: str) -> Optional[Callable]:
        """Returns the function associated with a given label"""
        func_path = self._storage_tasks.get(f"{self._namespace}.{label}")
        if func_path:
            module_path, func_name = func_path.rsplit(".", 1)
            module = importlib.import_module(module_path)
            return getattr(module, func_name)
        return None

    def storage_delete_tasks(self, label: str) -> Optional[Callable]:
        """Returns the function associated with a given label"""
        func_path = self._storage_delete_tasks.get(f"{self._namespace}.{label}")
        if func_path:
            module_path, func_name = func_path.rsplit(".", 1)
            module = importlib.import_module(module_path)
            return getattr(module, func_name)
        return None
    
    def storage_tasks_list(self) -> dict:
        return self._storage_tasks
    
    def storage_create_hooks(self, label: str) -> Optional[Callable]:
        """Returns the function associated with a given label"""
        func_path = self._storage_create_hooks.get(f"{self._namespace}.{label}")
        if func_path:
            module_path, func_name = func_path.rsplit(".", 1)
            module = importlib.import_module(module_path)
            return getattr(module, func_name)
        return None
    
    def storage_delete_hooks(self, label: str) -> Optional[Callable]:
        """Returns the function associated with a given label"""
        func_path = self._storage_delete_hooks.get(f"{self._namespace}.{label}")
        if func_path:
            module_path, func_name = func_path.rsplit(".", 1)
            module = importlib.import_module(module_path)
            return getattr(module, func_name)
        return None