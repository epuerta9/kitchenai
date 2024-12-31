from typing import Dict, Any
from kitchenai_rag_simple_bento.types import DependencyType

class DependencyManager:
    _instances: Dict[str, 'DependencyManager'] = {}
    
    def __init__(self, app_name: str):
        self.app_name = app_name
        self.dependencies: Dict[DependencyType, Any] = {}

    @classmethod
    def get_instance(cls, app_name: str) -> 'DependencyManager':
        if app_name not in cls._instances:
            cls._instances[app_name] = cls(app_name)
        return cls._instances[app_name]

    def register_dependency(self, dep_type: DependencyType, instance: Any) -> None:
        self.dependencies[dep_type] = instance

    def get_dependency(self, dep_type: DependencyType) -> Any:
        if dep_type not in self.dependencies:
            raise KeyError(f"Dependency {dep_type} not registered for app {self.app_name}")
        return self.dependencies[dep_type]

    @classmethod
    def reset_app(cls, app_name: str) -> None:
        if app_name in cls._instances:
            cls._instances[app_name].dependencies.clear() 