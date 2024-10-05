import pytest
from unittest.mock import patch, MagicMock
from kitchenai.client import KitchenClient  

@pytest.fixture
def kitchen_client():
    with KitchenClient(app_id="test-app", namespace="test-namespace") as client:
        yield client

def test_initialization(kitchen_client):
    assert kitchen_client.app_id == "test-app"
    assert kitchen_client._namespace == "test-namespace"

def test_dapr_id(kitchen_client):
    kitchen_client.dapr_id("new-app")
    assert kitchen_client.app_id == "new-app"

def test_namespace(kitchen_client):
    kitchen_client.namespace("new-namespace")
    assert kitchen_client._namespace == "new-namespace"

def test_create_path(kitchen_client):
    path = kitchen_client._create_path("query", "test-label")
    assert path == "/test-namespace/query/test-label"



@patch('kitchenai.client.DaprClient')
def test_query(mock_dapr_client, kitchen_client):
    mock_response = MagicMock()
    mock_response.text.return_value = '{"result": "Success"}'
    mock_dapr_client.return_value.invoke_method.return_value = mock_response

    result = kitchen_client.query("Test query", "test-label")

    assert result == '{"result": "Success"}'
    mock_dapr_client.return_value.invoke_method.assert_called_once_with(
        app_id="test-app",
        method_name="/test-namespace/query/test-label",
        data='{"query": "Test query"}',
        http_verb='POST',
        content_type='application/json'
    )

# @patch('kitchen_client.DaprClient')
# def test_invoke(mock_dapr_client, kitchen_client):
#     mock_response = MagicMock()
#     mock_response.text.return_value = '{"result": "Success"}'
#     mock_dapr_client.return_value.invoke_method.return_value = mock_response

#     result = kitchen_client.invoke({"key": "value"}, route="/test-route")

#     assert result == '{"result": "Success"}'
#     mock_dapr_client.return_value.invoke_method.assert_called_once_with(
#         app_id="test-app",
#         method_name="/test-route",
#         data='{"key": "value"}',
#         http_verb='POST',
#         content_type='application/json'
#     )

# @patch('kitchen_client.DaprClient')
# def test_invoke_error(mock_dapr_client, kitchen_client):
#     mock_dapr_client.return_value.invoke_method.side_effect = Exception("Test error")

#     with pytest.raises(Exception):
#         kitchen_client.invoke({"key": "value"}, route="/test-route")

# @patch('kitchen_client.DaprClient')
# def test_storage(mock_dapr_client, kitchen_client):
#     mock_response = MagicMock()
#     mock_response.text.return_value = '{"status": "stored"}'
#     mock_dapr_client.return_value.invoke_method.return_value = mock_response

#     result = kitchen_client.storage("save-data", key="test-key", value="test-value")

#     assert result == '{"status": "stored"}'
#     mock_dapr_client.return_value.invoke_method.assert_called_once_with(
#         app_id="test-app",
#         method_name="/test-namespace/storage/save-data",
#         data='{"key": "test-key", "value": "test-value"}',
#         http_verb='POST',
#         content_type='application/json'
#     )

# @patch('kitchen_client.DaprClient')
# def test_embedding(mock_dapr_client, kitchen_client):
#     mock_response = MagicMock()
#     mock_response.text.return_value = '{"embedding": [0.1, 0.2, 0.3]}'
#     mock_dapr_client.return_value.invoke_method.return_value = mock_response

#     result = kitchen_client.embedding("get-embedding", text="test text")

#     assert result == '{"embedding": [0.1, 0.2, 0.3]}'
#     mock_dapr_client.return_value.invoke_method.assert_called_once_with(
#         app_id="test-app",
#         method_name="/test-namespace/embedding/get-embedding",
#         data='{"text": "test text"}',
#         http_verb='POST',
#         content_type='application/json'
#     )

# @patch('kitchen_client.DaprClient')
# def test_runnable(mock_dapr_client, kitchen_client):
#     mock_response = MagicMock()
#     mock_response.text.return_value = '{"result": "runnable executed"}'
#     mock_dapr_client.return_value.invoke_method.return_value = mock_response

#     result = kitchen_client.runnable("execute-task", task="test task")

#     assert result == '{"result": "runnable executed"}'
#     mock_dapr_client.return_value.invoke_method.assert_called_once_with(
#         app_id="test-app",
#         method_name="/test-namespace/runnable/execute-task",
#         data='{"task": "test task"}',
#         http_verb='POST',
#         content_type='application/json'
#     )

# def test_context_manager():
#     with KitchenClient() as client:
#         assert client._dapr_client is not None
#     assert client._dapr_client is None

# @patch('kitchen_client.DaprClient')
# def test_retry_mechanism(mock_dapr_client, kitchen_client):
#     mock_response = MagicMock()
#     mock_response.text.return_value = '{"result": "Success after retry"}'
#     mock_dapr_client.return_value.invoke_method.side_effect = [
#         Exception("Transient error"),
#         Exception("Transient error"),
#         mock_response
#     ]

#     result = kitchen_client.query("Test query", "test-label")

#     assert result == '{"result": "Success after retry"}'
#     assert mock_dapr_client.return_value.invoke_method.call_count == 3