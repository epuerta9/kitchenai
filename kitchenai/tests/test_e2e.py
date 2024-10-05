import pytest
from kitchenai.client import KitchenClient  

"""
requires a real cookbook dapr container to be spun up
"""

@pytest.fixture
def kitchen_client():
    with KitchenClient(app_id="kitchenai", namespace="default") as client:
        yield client

def test_query_invoke(kitchen_client):
    resp = kitchen_client.query("query 1", "query-1")

    print(resp, flush=True)


def test_file_upload(kitchen_client):
    response = kitchen_client.upload_file("./tests/data/example.txt", "embed-1")

    print(response, flush=True)