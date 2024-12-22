from pydantic import BaseModel
from ..plugin import Plugin

# Define input and output schemas for ModifierPlugin
class ModifierInput(BaseModel):
    text: str  # Text to be modified
    metadata: dict = {}  # Additional metadata

class ModifierOutput(BaseModel):
    text: str  # The modified text
    metadata: dict = {}  # Additional metadata

class ModifierPlugin(Plugin):
    def __init__(self, signal, plugin_name):
        """
        Subclass for modifier plugins.
        Modifier plugins modify the input query and return a modified query.
        """
        super().__init__(
            signal,
            taxonomy="modifier",
            name=plugin_name,
            input_model=ModifierInput,
            output_model=ModifierOutput,
        )
