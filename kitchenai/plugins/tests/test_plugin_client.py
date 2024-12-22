from django.dispatch import Signal
from kitchenai.plugins.taxonomy.retriever import RetrieverPlugin, RetrieverInput, RetrieverOutput
from kitchenai.plugins.client import PluginClient
import pytest

# Define a test signal
test_signal = Signal()

# Mock Plugin A
class MockPluginA(RetrieverPlugin):
    def __init__(self, signal):
        super().__init__(signal, "plugin_a")
        self.handle_retrieve = self.handler(self.handle_retrieve)

    async def handle_retrieve(self, input: RetrieverInput) -> RetrieverOutput:
        print(f"MockPluginA: {input.label}")
        return RetrieverOutput(result="prompt a")

# Mock Plugin B
class MockPluginB(RetrieverPlugin):
    def __init__(self, signal):
        super().__init__(signal, "plugin_b")
        self.handle_retrieve = self.handler(self.handle_retrieve)

    async def handle_retrieve(self, input: RetrieverInput) -> RetrieverOutput:
        print(f"MockPluginB: {input.label}")
        return RetrieverOutput(result="prompt b")



@pytest.mark.asyncio
async def test_plugin_registration_via_signal():
    # Register plugins
    plugin_a = MockPluginA(test_signal)
    plugin_b = MockPluginB(test_signal)

    # Ensure both plugins are connected to the signal
    connected_receivers = test_signal._live_receivers(None)
    assert len(connected_receivers[1]) == 2
    assert any(getattr(receiver, "_plugin_name", None) == "plugin_a" for receiver in connected_receivers[1])
    assert any(getattr(receiver, "_plugin_name", None) == "plugin_b" for receiver in connected_receivers[1])



@pytest.mark.asyncio
async def test_signal_routing_by_plugin_name():
    # Register plugins
    plugin_a = MockPluginA(test_signal)
    plugin_b = MockPluginB(test_signal)

    # Create the client
    client = PluginClient(test_signal)

    # Route to Plugin A
    response_a = await client.send(plugin_name="plugin_a", taxonomy="retriever", label="prompt_managementA")
    print(f"response_a: {response_a}")

    assert response_a["result"] == "prompt a"

    # Route to Plugin B
    response_b = await client.send(plugin_name="plugin_b", taxonomy="retriever", label="prompt_managementB")
    assert response_b["result"] == "prompt b"


@pytest.mark.asyncio
async def test_missing_plugin_name():
    # Register Plugin A only
    MockPluginA(test_signal)

    # Create the client
    client = PluginClient(test_signal)

    # Attempt to route to a non-existent plugin
    try:
        response = await client.send(plugin_name="plugin_b", taxonomy="retriever", label="prompt_managementB")
    except Exception as e:
        response = e
    # Returns the original data if no handler matches
    assert isinstance(response, Exception)



@pytest.mark.asyncio
async def test_no_handlers_registered():
    # Ensure no plugins are registered
    test_signal.receivers.clear()

    # Create the client
    client = PluginClient(test_signal)

    # Attempt to send a query
    try:
        response = await client.send(taxonomy="retriever", label="prompt_managementA")
    except Exception as e:
        response = e
    assert isinstance(response, Exception)
