from django.test import TestCase
from ninja.testing import TestAsyncClient
from kitchenai_rag_simple_bento.kitchen import app  # Adjust this import to match your router location
from django.core.files.uploadedfile import SimpleUploadedFile
import pytest



class TestKitchenAIRoutes(TestCase):

    def setUp(self):
        self.client = TestAsyncClient()

    @pytest.mark.asyncio
    async def test_health_endpoint(self):
        query_data = {"query": "test health"}
        

        print(self.client)
        response = await self.client.post(
            "/api/v1/health",
            json=query_data
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("msg", response.json())

