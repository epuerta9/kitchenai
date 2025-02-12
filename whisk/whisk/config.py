from pathlib import Path
import yaml
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, ValidationError

class ConfigError(Exception):
    """Base exception for configuration errors"""
    pass

class ClientConfigError(ConfigError):
    """Raised when client configuration is invalid"""
    pass

class NatsConfig(BaseModel):
    url: str = "nats://localhost:4222"
    user: Optional[str] = "playground"
    password: Optional[str] = "kitchenai_playground"

class ClientConfig(BaseModel):
    id: str = Field(..., description="Client ID must be set via WHISK_CLIENT_ID")

class LLMConfig(BaseModel):
    cloud_api_key: Optional[str] = None

class ChromaConfig(BaseModel):
    path: str = "chroma_db"

class WhiskConfig(BaseModel):
    nats: NatsConfig
    client: ClientConfig
    llm: LLMConfig = LLMConfig()
    chroma: ChromaConfig = ChromaConfig()

    @classmethod
    def from_file(cls, path: str | Path) -> "WhiskConfig":
        """Load config from YAML file"""
        with open(path) as f:
            data = yaml.safe_load(f)
        return cls(**data)

    @classmethod 
    def from_env(cls) -> "WhiskConfig":
        """Load config from environment variables"""
        import os
        
        client_id = os.getenv("WHISK_CLIENT_ID")
        if not client_id:
            raise ClientConfigError(
                "WHISK_CLIENT_ID environment variable must be set. "
                "This is required to uniquely identify your client in the KitchenAI network."
            )

        try:
            return cls(
                nats=NatsConfig(
                    url=os.getenv("WHISK_NATS_URL", "nats://localhost:4222"),
                    user=os.getenv("WHISK_NATS_USER", "playground"),
                    password=os.getenv("WHISK_NATS_PASSWORD", "kitchenai_playground"),
                ),
                client=ClientConfig(
                    id=client_id
                ),
                llm=LLMConfig(
                    cloud_api_key=os.getenv("LLAMA_CLOUD_API_KEY")
                ),
                chroma=ChromaConfig(
                    path=os.getenv("WHISK_CHROMA_PATH", "chroma_db")
                )
            )
        except ValidationError as e:
            raise ClientConfigError(f"Invalid configuration: {str(e)}") 