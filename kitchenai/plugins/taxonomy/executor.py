from pydantic import BaseModel
from ..plugin import Plugin

# Define input and output schemas for ExecutorPlugin
class ExecutorInput(BaseModel):
    query: str  # The original query string
    metadata: dict = {}  # Additional metadata


class ExecutorOutput(BaseModel):
    query: str  # The modified query string
    metadata: dict = {}  # Additional metadata

class ExecutorPlugin(Plugin):
    def __init__(self, signal, plugin_name):
        """
        Subclass for Executor plugins.
        Executor plugins modify the input query and return a modified query.
        """
        super().__init__(
            signal,
            taxonomy="executor",
            name=plugin_name,
            input_model=ExecutorInput,
            output_model=ExecutorOutput,
        )
