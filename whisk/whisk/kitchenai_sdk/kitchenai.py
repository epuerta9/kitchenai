from whisk.kitchenai_sdk.taxonomy.query import QueryTask
from whisk.kitchenai_sdk.taxonomy.storage import StorageTask
from whisk.kitchenai_sdk.taxonomy.embeddings import EmbedTask
from whisk.kitchenai_sdk.taxonomy.agent import AgentTask
from .base import DependencyManager
from .schema import DependencyType
from typing import Any


class KitchenAIApp:
    def __init__(self, namespace: str = "default", version: str = "0.0.1"):
        self.namespace = namespace
        self.version = version
        self.client_type = 'bento_box'
        self.client_description = 'Bento box'
        self.manager = DependencyManager()
        self.query = QueryTask(namespace, self.manager)
        self.storage = StorageTask(namespace, self.manager)
        self.embeddings = EmbedTask(namespace, self.manager)
        self.agent = AgentTask(namespace, self.manager)
        self._mounted_apps = {}

    def mount_app(self, prefix: str, app: 'KitchenAIApp'):
        """Mount a sub-app and merge its handlers with prefixed labels"""
        # Merge dependencies
        for dep_type, dep in app.manager._dependencies.items():
            if dep_type not in self.manager._dependencies:
                self.manager.register_dependency(dep_type, dep)
        
        # Store mounted app
        self._mounted_apps[prefix] = app
        
        # Merge handlers with prefixed labels
        query_tasks = app.query.list_tasks()
        if isinstance(query_tasks, list):
            # Convert list to dict using task.__name__ as key
            query_tasks = {task.__name__: task for task in query_tasks}
        for label, handler in query_tasks.items():
            prefixed_label = f"{prefix}.{label}"
            self.query.register_task(prefixed_label, handler)
            
        storage_tasks = app.storage.list_tasks()
        if isinstance(storage_tasks, list):
            storage_tasks = {task.__name__: task for task in storage_tasks}
        for label, handler in storage_tasks.items():
            prefixed_label = f"{prefix}.{label}"
            self.storage.register_task(prefixed_label, handler)
            
        embed_tasks = app.embeddings.list_tasks()
        if isinstance(embed_tasks, list):
            embed_tasks = {task.__name__: task for task in embed_tasks}
        for label, handler in embed_tasks.items():
            prefixed_label = f"{prefix}.{label}"
            self.embeddings.register_task(prefixed_label, handler)

    def register_dependency(self, dep_type, dep):
        """Register dependency and propagate to mounted apps"""
        self.manager.register_dependency(dep_type, dep)
        for app in self._mounted_apps.values():
            if dep_type not in app.manager._dependencies:
                app.manager.register_dependency(dep_type, dep)

    def set_manager(self, manager):
        """Update the manager for the app and all tasks."""
        self.manager = manager
        self.query._manager = manager
        self.storage._manager = manager
        self.embeddings._manager = manager
        self.agent._manager = manager

    def to_dict(self):
        """Generate a summary of all registered tasks."""
        return {
            "namespace": self.namespace,
            "query_handlers": list(self.query.list_tasks().keys()),
            "storage_handlers": list(self.storage.list_tasks().keys()),
            "embed_handlers": list(self.embeddings.list_tasks().keys()),
            "agent_handlers": list(self.agent.list_tasks().keys()),
        }
