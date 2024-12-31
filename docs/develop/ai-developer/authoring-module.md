I'll help you modify the `with_dependencies` decorator to inject dependencies as typed arguments rather than keyword arguments. Here's how we can update the code:

```python:kitchenai/contrib/kitchenai_sdk/base.py
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
```

Key changes made:
1. Changed `get_dependencies()` to return a list instead of a dict
2. Modified the wrappers to use `*deps` instead of `**deps` to pass dependencies as positional arguments

Now you can use the decorator like this:

```python
@task.with_dependencies(DependencyType.LLM, DependencyType.VECTORSTORE)
async def my_function(self, llm, vectorstore):
    # llm will be the LLM dependency
    # vectorstore will be the VECTORSTORE dependency
    ...
```

The dependencies will be injected in the same order as specified in the decorator. Make sure your function parameters match the order and types of dependencies you're requesting in the decorator.
