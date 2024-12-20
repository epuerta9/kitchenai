# import pytest
# from django.test.client import Client

# @pytest.fixture
# def api_client():
#     """Fixture for API testing"""
#     from django.test.client import Client
#     return Client() 



# @pytest.mark.django_db
# def test_index_page_200():
#     response = Client().get("/")
#     assert response.status_code == 200