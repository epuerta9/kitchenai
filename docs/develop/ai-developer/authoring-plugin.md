Here's a documentation section for creating Evaluator plugins:

```markdown
# Creating Plugins

## Evaluator Plugins

Evaluator plugins allow you to process and modify queries, as well as display metrics and analytics through widgets.

### Basic Structure

To create an evaluator plugin, inherit from `QueryEvaluatorPlugin`:

```python
from kitchenai.plugins.taxonomy.evaluator import (
    QueryEvaluatorPlugin,
    QueryEvaluatorInput,
    QueryEvaluatorOutput
)

class MyEvaluatorPlugin(QueryEvaluatorPlugin):
    def __init__(self, signal):
        super().__init__(signal, "my_evaluator")
    
    async def evaluate(self, input: QueryEvaluatorInput) -> QueryEvaluatorOutput:
        # Your evaluation logic here
        return QueryEvaluatorOutput(
            query=modified_query,
            metadata={"some": "metadata"}
        )
```

### Adding Widgets

Evaluator plugins can provide two types of widgets:
- `chat_metric_widget`: For displaying metrics for individual chat interactions
- `aggregate_chat_metric_widget`: For displaying aggregated metrics across multiple chats

To enable widgets, use the `Meta` class:

```python
class MyEvaluatorPlugin(QueryEvaluatorPlugin):
    class Meta:
        chat_metric_widget = True
        aggregate_chat_metric_widget = True
    
    def __init__(self, signal):
        super().__init__(signal, "my_evaluator")
    
    async def chat_metric_widget(self, chat_metric) -> str:
        """
        Return template path for individual chat metric widget
        """
        return "my_plugin/chat_metric_widget.html"
    
    async def aggregate_chat_metric_widget(self, metrics) -> str:
        """
        Return template path for aggregated metrics widget
        """
        return "my_plugin/aggregate_widget.html"
    
    async def evaluate(self, input: QueryEvaluatorInput) -> QueryEvaluatorOutput:
        # Your evaluation logic here
        pass
```

### Widget Requirements

- If you enable a widget in `Meta`, you must implement its corresponding method
- Widget methods should return a template path as a string
- Templates should be placed in your plugin's templates directory
- Widget methods are async to support database operations if needed

### Input/Output Schema

- `QueryEvaluatorInput`: Contains the query, response, and retrieval context
- `QueryEvaluatorOutput`: Contains the modified query and optional metadata

```python
# Input schema fields
input.query: str              # The original query
input.response: str           # The response from the retriever
input.retrieval_context: list # The context used for retrieval
input.metadata: dict          # Additional metadata

# Output schema fields
output.query: str            # The modified query
output.metadata: dict = {}   # Optional metadata
```
```

This documentation:
1. Explains the basic structure of evaluator plugins
2. Shows how to add and implement widgets
3. Details the requirements for widgets
4. Describes the input/output schema
5. Provides clear examples for implementation
