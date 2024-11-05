from ninja import Router
import functools
import logging
import asyncio
from django.http import StreamingHttpResponse

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class KitchenAIApp:
    def __init__(self, router: Router = None, namespace: str = 'default'):
        self._namespace = namespace
        self._router = router if router else Router()

    def _create_decorator(self, route_type: str, method: str, label: str, streaming=False):
        def decorator(func, **route_kwargs):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                if streaming:
                    # This wrapper will call the async generator function and yield its items in an HTTP streaming response
                    async def event_generator():
                        async for event in func(*args, **kwargs):
                            yield event

                    return StreamingHttpResponse(
                        event_generator(),
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

    def storage(self, label: str, **route_kwargs):
        return self._create_decorator('storage', "POST", label)

    def embedding(self, label: str, **route_kwargs):
        return self._create_decorator('embedding', "POST", label)

    def runnable(self, label: str, streaming=False, **route_kwargs):
        # Allows setting streaming=True to enable streaming responses
        return self._create_decorator('runnable', "POST", label, streaming=streaming)

    def agent(self, label: str, **route_kwargs):
        return self._create_decorator('agent', "POST", label)

