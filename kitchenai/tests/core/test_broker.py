import pytest
from kitchenai.core.broker import whisk
from whisk.kitchenai_sdk.nats_schema import StorageRequestMessage
from faststream.nats import TestNatsBroker
import uuid
import time

@pytest.mark.asyncio
async def test_mock_nats():
    """Test with mock NATS broker"""
    async with TestNatsBroker(whisk.broker) as test_broker:
        # Replace the real broker temporarily
        original_broker = whisk.broker
        whisk.broker = test_broker
        
        try:
            # Simple publish test
            test_message = StorageRequestMessage(
                id=1,
                name="test.txt",
                label="test_label",
                data=b"",
                metadata={"test": "data"},
                request_id=str(uuid.uuid4()),
                timestamp=time.time(),
                client_id="test-client"
            )
            
            await whisk.store_message(test_message)
            print("Mock broker test: Message published successfully")
            
        finally:
            whisk.broker = original_broker

@pytest.mark.asyncio
async def test_real_nats():
    """Test with real NATS broker"""
    try:
        # Start the broker
        await whisk.broker.start()
        
        # Simple publish test
        test_message = StorageRequestMessage(
            id=1,
            name="test.txt",
            label="test_label",
            data=b"",
            metadata={"test": "data"},
            request_id=str(uuid.uuid4()),
            timestamp=time.time(),
            client_id="test-client"
        )
        
        await whisk.store_message(test_message)
        print("Real broker test: Message published successfully")
        
    finally:
        await whisk.broker.close() 