from collections.abc import Callable
import functools
import importlib


class KitchenAITask:
    def __init__(self, namespace: str):
        self.namespace = namespace
        self._tasks = {}

    def register_task(self, label: str, func: Callable):
        task_key = f"{self.namespace}.{label}"
        self._tasks[task_key] = func
        return func

    def get_task(self, label: str) -> Callable | None:
        task_key = f"{self.namespace}.{label}"
        return self._tasks.get(task_key)

    def list_tasks(self) -> dict:
        return list(self._tasks.keys())
