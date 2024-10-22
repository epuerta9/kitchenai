import asyncio
import functools
import logging

from ninja import Router

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class KitchenAIApp:
    def __init__(self, router: Router = None, namespace: str = 'default'):
        self._namespace = namespace
        self._router = router if router else Router()

    # Helper method to create a decorator for a given route type
    def _create_decorator(self, route_type: str, method: str, label: str):
        def decorator(func, **route_kwargs):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                if asyncio.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                else:
                    loop = asyncio.get_event_loop()
                return await loop.run_in_executor(None, lambda: func(*args, **kwargs))

            # Define the path for the route using the namespace and label
            route_path = f"/{route_type}/{label}"

            # Register the route using add_api_operation
            self._router.add_api_operation(
                path=route_path,
                methods=[method],  # Customize as needed (GET, PUT, etc.)
                view_func=wrapper,
                **route_kwargs  # Pass the custom kwargs defined by the user in the decorator
            )
            logger.debug(f"Registered route: {route_path}")
            return wrapper
        return decorator

    # Query decorator
    def query(self, label: str, **route_kwargs):
        return self._create_decorator('query',"POST", label)

    # Storage decorator
    def storage(self, label: str, **route_kwargs):
        return self._create_decorator('storage', "POST", label)

    # Embedding decorator
    def embedding(self, label: str, **route_kwargs):
        return self._create_decorator('embedding', "POST", label)

    # Runnable decorator (for chaining multiple tasks)
    def runnable(self, label: str, **route_kwargs):
        return self._create_decorator('runnable', "POST", label)
