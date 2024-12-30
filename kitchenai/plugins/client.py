from django.dispatch import Signal
class PluginClient:
    def __init__(self, signal: Signal):
        """
        Initialize the PluginClient with a specific signal.
        """
        self.signal = signal

    async def send(self, plugin_name: str = None, taxonomy: str = None,**kwargs):
        """
        Send a signal targeting a specific plugin or taxonomy.
        :param plugin_name: The specific plugin to invoke.
        :param taxonomy: Optional taxonomy to filter handlers.
        :param kwargs: Data to send to handlers.
        :return: The response from the specified handler or the original data.
        """
        for receiver in self.signal._live_receivers(None)[1]:
            if plugin_name and getattr(receiver, "_plugin_name", None) != plugin_name:
                continue  # Skip handlers that don't match the plugin name
            if taxonomy and getattr(receiver, "_taxonomy", None) != taxonomy:
                continue  # Skip handlers that don't match the taxonomy
            response = await receiver(None, **kwargs)
            if response:
                return response  # Return the first valid response

        if taxonomy == "retriever":
            #we are expecting a response
            raise Exception("No handlers responded")
        

#clients
# response_execute_client = PluginClient(response_execute)