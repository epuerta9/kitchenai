import pytest
from unittest.mock import AsyncMock, patch
from faststream import FastStream
from faststream.nats import TestNatsBroker, NatsBroker
from django.conf import settings
from kitchenai.core.broker.whisk import create_whisk

@pytest.fixture(autouse=True)
async def mock_signals():
    """Disable all signals during tests"""
    with patch('django.db.models.signals.post_save.send', new=AsyncMock()) as mock_post_save:
        yield mock_post_save

@pytest.fixture(autouse=True, scope="session")
async def test_whisk():
    """Create a test whisk instance with TestNatsBroker"""
    # Create the test broker setup
    real_broker = NatsBroker(url=settings.WHISK_SETTINGS["nats_url"])
    test_broker = TestNatsBroker(real_broker)
    
    # Create FastStream app with test broker
    app = FastStream(broker=test_broker)
    
    # Create whisk instance with our test app
    test_whisk = create_whisk(app=app)
    
    # Patch the global whisk instance before Django loads
    with patch('kitchenai.core.broker.whisk.whisk', test_whisk):
        yield test_whisk

@pytest.fixture(autouse=True)
async def mock_broker_lifespan():
    """Mock the broker lifespan context manager"""
    with patch('kitchenai.asgi.broker_lifespan') as mock_lifespan:
        mock_lifespan.return_value.__aenter__ = AsyncMock()
        mock_lifespan.return_value.__aexit__ = AsyncMock()
        yield mock_lifespan

@pytest.fixture(autouse=True)
async def mock_whisk():
    """Mock the whisk client"""
    mock_whisk = AsyncMock()
    mock_whisk.store_message = AsyncMock()
    
    with patch('kitchenai.core.broker.whisk.whisk', mock_whisk):
        yield mock_whisk 