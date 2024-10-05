from fastapi import FastAPI, Request, Depends
from typing import Optional, Callable, Any
from pydantic import BaseModel
import inspect

class KitchenAIApp:
    """
    Wraps FastAPI with KitchenAI

    Args:
        app_instance: The FastAPI instance to wrap.
    """

    def __init__(self, app_instance: FastAPI = None, namespace: Optional[str] = 'default'):
        self._namespace = namespace
        self._app = app_instance if app_instance else FastAPI()
        self._metadata = {}

        self._app.add_api_route(
            f'/{namespace}/meta', self._get_metadata, methods=['GET'], tags=[self._namespace]
        )

    def _get_metadata(self):
        return self._metadata

    def _create_decorator(self, route_type: str, label: str) -> Callable:
        def decorator(func: Callable):
            is_async = inspect.iscoroutinefunction(func)

            async def async_wrapper(request: Request):

                return await func(request)

            def sync_wrapper(request: Request):

                return func(request)

            wrapper = async_wrapper if is_async else sync_wrapper
            route = f'/{self._namespace}/{route_type}/{label}'
            self._app.add_api_route(route, wrapper, methods=['POST'], tags=[label])
            
            if route_type not in self._metadata:
                self._metadata[route_type] = {}
            self._metadata[route_type][label] = route

            return func
        return decorator

    def query(self, label: str):
        return self._create_decorator('query', label)

    def storage(self, label: str):
        return self._create_decorator('storage', label)

    def embedding(self, label: str):
        return self._create_decorator('embedding', label)

    def runnable(self, label: str):
        return self._create_decorator('runnable', label)