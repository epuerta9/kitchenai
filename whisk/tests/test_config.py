import pytest
import os
from whisk.config import WhiskConfig, ClientConfigError

def test_config_requires_client_id():
    """Test that config raises error when WHISK_CLIENT_ID is not set"""
    # Ensure WHISK_CLIENT_ID is not set
    if "WHISK_CLIENT_ID" in os.environ:
        del os.environ["WHISK_CLIENT_ID"]
    
    with pytest.raises(ClientConfigError) as exc_info:
        WhiskConfig.from_env()
    
    assert "WHISK_CLIENT_ID environment variable must be set" in str(exc_info.value)

def test_config_loads_with_client_id():
    """Test that config loads successfully when WHISK_CLIENT_ID is set"""
    os.environ["WHISK_CLIENT_ID"] = "test_client"
    
    config = WhiskConfig.from_env()
    assert config.client.id == "test_client"

def test_config_with_custom_values():
    """Test that config loads custom values from environment"""
    os.environ.update({
        "WHISK_CLIENT_ID": "test_client",
        "WHISK_NATS_URL": "nats://custom:4222",
        "WHISK_NATS_USER": "custom_user",
        "WHISK_NATS_PASSWORD": "custom_pass",
        "WHISK_CHROMA_PATH": "custom_path"
    })
    
    config = WhiskConfig.from_env()
    assert config.client.id == "test_client"
    assert config.nats.url == "nats://custom:4222"
    assert config.nats.user == "custom_user"
    assert config.nats.password == "custom_pass"
    assert config.chroma.path == "custom_path" 