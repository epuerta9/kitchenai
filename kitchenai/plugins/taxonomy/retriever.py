from pydantic import BaseModel
from ..plugin import Plugin

# Define input and output schemas for RetrieverPlugin
class RetrieverInput(BaseModel):
    label: str  # Query to retrieve results for
    metadata: dict = {}  # Optional metadata dictionary with empty dict default


class RetrieverOutput(BaseModel):
    result: str  # The retrieved result
    metadata: dict = {}  # Optional metadata dictionary with empty dict default


class RetrieverPlugin(Plugin):
    def __init__(self, signal, plugin_name):
        """
        Subclass for retriever plugins.
        Retriever plugins take a query and return relevant results from a data source.
        """
        super().__init__(
            signal,
            taxonomy="retriever",
            name=plugin_name,
            input_model=RetrieverInput,
            output_model=RetrieverOutput,
        )
