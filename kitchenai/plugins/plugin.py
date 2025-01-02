from pydantic import BaseModel, ValidationError
import logging

logger = logging.getLogger(__name__)

class Plugin:
    def __init__(self, signal, taxonomy, name, sender=None, input_model: BaseModel = None, output_model: BaseModel = None):
        """
        Base class for plugins.
        :param signal: The signal to which the plugin registers its handler.
        :param taxonomy: Taxonomy or category for the plugin handler.
        :param name: Unique name for the plugin.
        :param input_model: Pydantic model for input validation.
        :param output_model: Pydantic model for output validation.
        """
        self.signal = signal
        self.sender = sender
        self.taxonomy = taxonomy
        self.name = name
        self.input_model = input_model
        self.output_model = output_model

    @property
    def plugin_name(self):
        """Expose the plugin name."""
        return self.name

    def handler(self, func):
        """
        Decorator to define a plugin handler and automatically register it.
        Validates input and output using Pydantic models.
        """
        async def wrapped_handler(sender, **kwargs):
            # Validate and parse input

            validated_input = self.input_model(**kwargs)

            # Execute the original function
            result = await func(validated_input)

            # If the result is already a Pydantic model, return it or its dict
            if isinstance(result, self.output_model):
                return result.model_dump()

            # Validate and parse output
            if self.output_model:
                try:
                    validated_output = self.output_model(**result)
                    return validated_output.model_dump()
                except ValidationError as e:
                    raise ValueError(f"Invalid output for handler {func.__name__}: {e}")
            #send it to the next signal if needed

        # Attach metadata to the handler
        wrapped_handler._taxonomy = self.taxonomy
        wrapped_handler._plugin_name = self.name

        # Register the wrapped handler to the signal
        self.signal.connect(wrapped_handler, sender=self.sender)
        return wrapped_handler
