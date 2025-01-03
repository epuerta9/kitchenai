from pydantic import BaseModel
from kitchenai.contrib.kitchenai_sdk.schema import QueryBaseResponseSchema
from ..plugin import Plugin
from typing import Optional, Type
from abc import abstractmethod

# Define input and output schemas for EvaluatorPlugin

class QueryEvaluatorInput(QueryBaseResponseSchema):
    source_id: int



class QueryEvaluatorOutput(BaseModel):
    query: Optional[str] = None  # The modified query string
    metadata: Optional[dict] = None  # Additional metadata


class EvaluatorPluginMeta:
    """
    Meta class for configuring plugin widgets
    """
    chat_metric_widget: bool = False
    aggregate_chat_metric_widget: bool = False

class QueryEvaluatorPlugin(Plugin):
    def __init__(self, signal, sender, plugin_name):
        """
        Subclass for Evaluator plugins.
        Evaluator plugins modify the input query and return a modified query.
        """

        super().__init__(
            signal,
            taxonomy="evaluator",
            name=plugin_name,
            sender=sender,
            input_model=QueryEvaluatorInput,  # Using our new input model
            output_model=QueryEvaluatorOutput,
        )
        
        # Get Meta attributes or use defaults
        meta = getattr(self, 'Meta', EvaluatorPluginMeta)
        self.has_chat_metric_widget = getattr(meta, 'chat_metric_widget', False)
        self.has_aggregate_widget = getattr(meta, 'aggregate_chat_metric_widget', False)
        
        # Validate that required methods exist if widgets are enabled
        if self.has_chat_metric_widget and not hasattr(self, 'get_chat_metric_widget'):
            raise NotImplementedError(
                f"Plugin {plugin_name} has chat_metric_widget enabled but doesn't implement chat_metric_widget()"
            )
            
        if self.has_aggregate_widget and not hasattr(self, 'get_aggregate_chat_metric_widget'):
            raise NotImplementedError(
                f"Plugin {plugin_name} has aggregate_chat_metric_widget enabled but doesn't implement aggregate_chat_metric_widget()"
            )

    def get_available_widgets(self) -> dict:
        """
        Returns a dictionary of available widgets for this plugin
        """
        widgets = {}
        if self.has_chat_metric_widget:
            widgets['chat_metric'] = self.get_chat_metric_widget
        if self.has_aggregate_widget:
            widgets['aggregate'] = self.get_aggregate_chat_metric_widget
        return widgets

    @abstractmethod
    async def evaluate(self, input: QueryEvaluatorInput) -> QueryEvaluatorOutput:
        """
        Evaluate the input and return an EvaluatorOutput
        """
        pass