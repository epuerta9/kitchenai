from pydantic import BaseModel
from ..plugin import Plugin

# Define input and output schemas for GeneratorPlugin
class GeneratorInput(BaseModel):
    query: str  # The original query string
    metadata: dict = {}  # Additional metadata      

class GeneratorOutput(BaseModel):
    query: str  # The modified query string
    metadata: dict = {}  # Additional metadata

class GeneratorPlugin(Plugin):
    def __init__(self, signal, plugin_name):
        """
        Subclass for Generator plugins.
        Generator plugins modify the input query and return a modified query.
        """
        super().__init__(
            signal,
            taxonomy="generator",
            name=plugin_name,
            input_model=GeneratorInput,
            output_model=GeneratorOutput,
        )
