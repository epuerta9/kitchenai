from kitchenai.plugins.taxonomy.evaluator import QueryEvaluatorPlugin, QueryEvaluatorInput, QueryEvaluatorOutput
from .models import DataSet, Data
from .utils import is_enabled
import logging
logger = logging.getLogger(__name__)


class DeepEvalPlugin(QueryEvaluatorPlugin):

    class Meta:
        chat_metric_widget = True
        aggregate_chat_metric_widget = True

    def __init__(self, signal, sender, plugin_name: str):
        super().__init__(signal, sender, plugin_name)
        self.evaluator = self.handler(self.evaluate)
         #self decorator to register the evaluate method

    def get_chat_metric_widget(self) -> str:
        return f"deepeval:chat_widget_for_source"

    def get_aggregate_chat_metric_widget(self) -> str:
        return "deepeval_plugin/widgets/aggregate_chat_widget.html"

    async def evaluate(self, input: QueryEvaluatorInput) -> QueryEvaluatorOutput:
        """
        Store the input to start building the dataset
        """
        if is_enabled():
            if not input.metadata:
                return QueryEvaluatorOutput()
            if input.metadata.get("dataset_id"):
                dataset, created = await DataSet.objects.aget_or_create(id=input.metadata.get("dataset_id"))
            else:
                dataset, created = await DataSet.objects.aget_or_create(name="default")
            if dataset.enabled:
                if input.retrieval_context:
                    retrieval_context = [source.model_dump() for source in input.retrieval_context]
                    data = Data(input=input.input, source_id=input.source_id, output=input.output, retrieval_context=retrieval_context, dataset=dataset)
                    await data.asave()
                else:
                    data = Data(input=input.input, source_id=input.source_id, output=input.output, dataset=dataset)
                    await data.asave()

        else:
            logger.info("DeepEval is not enabled")

        return QueryEvaluatorOutput(query=input.input, metadata=input.metadata)

