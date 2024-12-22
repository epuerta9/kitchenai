from kitchenai.plugins.taxonomy.evaluator import EvaluatorPlugin, EvaluatorInput
from .models import DataSet, Data

class DeepEvalPlugin(EvaluatorPlugin):
    def __init__(self, signal, plugin_name: str):
        super().__init__(signal, plugin_name)
        self.evaluator = self.handler(self.evaluate) #self decorator to register the evaluate method


    async def evaluate(self, input: EvaluatorInput) -> dict:
        """
        Store the input to start building the dataset
        """
        if input.metadata.get("dataset_id"):
            dataset = await DataSet.objects.aget(id=input.metadata.get("dataset_id"))
        else:
            dataset = await DataSet.objects.aget(name="default")

        if dataset.enabled:
            data = Data(input=input.input, output=input.output, retrieval_context=input.retrieval_context, dataset=dataset)
            await data.asave()


    def on_load(self):
        """
        Register the plugin. and set up the db tables
        """
        
        
        # Create default dataset if it doesn't exist
        if not DataSet.objects.filter(name="default").exists():
            DataSet.objects.create(name="default")