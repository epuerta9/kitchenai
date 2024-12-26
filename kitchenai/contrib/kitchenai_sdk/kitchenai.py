import asyncio
import functools
import importlib
import logging
from collections.abc import Callable
from ninja import Router

from kitchenai.contrib.kitchenai_sdk.taxonomy.query import QueryTask
from kitchenai.contrib.kitchenai_sdk.taxonomy.storage import StorageTask
from kitchenai.contrib.kitchenai_sdk.taxonomy.embeddings import EmbedTask
from kitchenai.contrib.kitchenai_sdk.taxonomy.agent import AgentTask

from kitchenai.broker import broker

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class KitchenAIApp:
    def __init__(self, namespace: str = "default"):
        self.namespace = namespace
        self.query = QueryTask(namespace)
        self.storage = StorageTask(namespace)
        self.embeddings = EmbedTask(namespace)
        self.agent = AgentTask(namespace)
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
