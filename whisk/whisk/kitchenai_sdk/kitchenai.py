from whisk.kitchenai_sdk.taxonomy.query import QueryTask
from whisk.kitchenai_sdk.taxonomy.storage import StorageTask
from whisk.kitchenai_sdk.taxonomy.embeddings import EmbedTask
from whisk.kitchenai_sdk.taxonomy.agent import AgentTask


class KitchenAIApp:
    def __init__(self, namespace: str = "default", manager = None, version: str = "0.0.1"):
        self.namespace = namespace
        self.manager = manager
        self.version = version
        self.client_type = 'bento_box'
        self.client_description = 'Bento box'
        self.query = QueryTask(namespace, manager)
        self.storage = StorageTask(namespace, manager)
        self.embeddings = EmbedTask(namespace, manager)
        self.agent = AgentTask(namespace, manager)
        self._default_hook = "kitchenai.contrib.kitchenai_sdk.hooks.default_hook"

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
            "query_handlers": self.query.list_tasks(),
            "storage_handlers": self.storage.list_tasks(),
            "embed_handlers": self.embeddings.list_tasks(),
            "agent_handlers": self.agent.list_tasks(),
        }
