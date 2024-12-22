from pydantic import BaseModel
from ..plugin import Plugin

# Define input and output schemas for EvaluatorPlugin
class EvaluatorInput(BaseModel):
    query: str  # The original query string
    response: str  # The response from the retriever
    retrieval_context: list[str]  # The context retrieved from the retriever
    metadata: dict = {}  # Additional metadata


class EvaluatorOutput(BaseModel):
    query: str  # The modified query string
    metadata: dict = {}  # Additional metadata


class EvaluatorPlugin(Plugin):
    def __init__(self, signal, plugin_name):
        """
        Subclass for Evaluator plugins.
        Evaluator plugins modify the input query and return a modified query.
        """
        super().__init__(
            signal,
            taxonomy="evaluator",
            name=plugin_name,
            input_model=EvaluatorInput,
            output_model=EvaluatorOutput,
        )
