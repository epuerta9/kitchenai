from unittest.mock import Mock
from unittest.mock import patch

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client


@pytest.fixture
def api_client():
    return Client()

@pytest.fixture
def mock_chroma_client():
    with patch('chromadb.EphemeralClient') as mock:
        yield mock

@pytest.fixture
def mock_llm():
    with patch('llama_index.llms.openai.OpenAI') as mock:
        yield mock

class TestAIClient:

    @pytest.mark.asyncio
    @patch('llama_index.core.VectorStoreIndex.from_documents')
    @patch('llama_index.core.SimpleDirectoryReader')
    async def test_storage_endpoint(self, mock_reader, mock_index, api_client):
        # Create a mock file
        file_content = b"This is a test document"
        uploaded_file = SimpleUploadedFile(
            "test.txt",
            file_content,
            content_type="text/plain"
        )

        # Mock the SimpleDirectoryReader
        mock_documents = [Mock()]
        mock_reader.return_value.load_data.return_value = mock_documents

        # Make the request
        response = api_client.post(
            "/api/storage",
            {"file": uploaded_file},
            format="multipart"
        )

        # Assertions
        assert response.status_code == 200
        assert response.json() == {"msg": "ok"}

        # Verify that the vector store was properly called
        mock_index.assert_called_once()

    @pytest.mark.asyncio
    @patch('llama_index.core.VectorStoreIndex.from_vector_store')
    async def test_query_endpoint(self, mock_index, api_client, mock_llm):
        # Mock the chat engine response
        mock_chat_engine = Mock()
        mock_response = Mock()
        mock_response.response = "This is a test response"
        mock_chat_engine.achat.return_value = mock_response

        mock_index.return_value.as_chat_engine.return_value = mock_chat_engine

        # Make the request
        query_data = {"query": "What is the meaning of life?"}
        response = api_client.post(
            "/api/query",
            query_data,
            content_type="application/json"
        )

        # Assertions
        assert response.status_code == 200
        assert response.json() == {"msg": "This is a test response"}

        # Verify that the chat engine was called with correct parameters
        mock_chat_engine.achat.assert_called_once_with(query_data["query"])

    @pytest.mark.asyncio
    async def test_query_endpoint_invalid_input(self, api_client):
        # Test with missing query field
        response = api_client.post(
            "/api/query",
            {},
            content_type="application/json"
        )
        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    @patch('llama_index.core.VectorStoreIndex.from_vector_store')
    async def test_query_endpoint_error_handling(self, mock_index, api_client):
        # Mock an error in the chat engine
        mock_chat_engine = Mock()
        mock_chat_engine.achat.side_effect = Exception("Test error")
        mock_index.return_value.as_chat_engine.return_value = mock_chat_engine

        # Make the request
        query_data = {"query": "What is the meaning of life?"}
        response = api_client.post(
            "/api/query",
            query_data,
            content_type="application/json"
        )

        # Assertions
        assert response.status_code == 500
