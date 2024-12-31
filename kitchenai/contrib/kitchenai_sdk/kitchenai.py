import logging


from kitchenai.contrib.kitchenai_sdk.taxonomy.query import QueryTask
from kitchenai.contrib.kitchenai_sdk.taxonomy.storage import StorageTask
from kitchenai.contrib.kitchenai_sdk.taxonomy.embeddings import EmbedTask
from kitchenai.contrib.kitchenai_sdk.taxonomy.agent import AgentTask


# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class KitchenAIApp:
    def __init__(self, namespace: str = "default", manager = None):
        self.namespace = namespace
        self.query = QueryTask(namespace, manager)
        self.storage = StorageTask(namespace, manager)
        self.embeddings = EmbedTask(namespace, manager)
        self.agent = AgentTask(namespace, manager)
        self._default_hook = "kitchenai.contrib.kitchenai_sdk.hooks.default_hook"


    def to_dict(self):
        """Generate a summary of all registered tasks."""
        return {
            "namespace": self.namespace,
            "query_handlers": self.query.list_tasks(),
            "storage_handlers": self.storage.list_tasks(),
            "embed_handlers": self.embeddings.list_tasks(),
            "agent_handlers": self.agent.list_tasks(),
        }
