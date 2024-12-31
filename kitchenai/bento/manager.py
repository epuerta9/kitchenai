from typing import Any
from .types import DependencyType

class DependencyManager:
    _instances = {}

    @classmethod
    def get_instance(cls, app_name: str) -> 'DependencyManager':
        if app_name not in cls._instances:
            cls._instances[app_name] = cls(app_name)
        return cls._instances[app_name]

    def __init__(self, app_name: str):
        self.app_name = app_name
        self._dependencies = {}

    def register_dependency(self, dep_type: DependencyType, instance: Any):
        self._dependencies[dep_type] = instance

    def get_dependency(self, dep_type: DependencyType) -> Any:
        if dep_type not in self._dependencies:
            raise ValueError(f"Dependency {dep_type} not registered for app {self.app_name}")
        return self._dependencies[dep_type]