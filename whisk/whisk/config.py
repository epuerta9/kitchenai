from pathlib import Path
import yaml
from typing import Optional, Dict, Any
from pydantic import BaseModel

class NatsConfig(BaseModel):
    url: str
    user: str 
    password: str

class ClientConfig(BaseModel):
    id: str

class LLMConfig(BaseModel):
    cloud_api_key: Optional[str] = None

class ChromaConfig(BaseModel):
    path: str

class WhiskConfig(BaseModel):
    nats: NatsConfig
    client: ClientConfig
    llm: Optional[LLMConfig] = None
    chroma: Optional[ChromaConfig] = None

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
        return cls(
            nats=NatsConfig(
                url=os.getenv("WHISK_NATS_URL", "nats://localhost:4222"),
                user=os.getenv("WHISK_NATS_USER", "playground"),
                password=os.getenv("WHISK_NATS_PASSWORD", "kitchenai_playground"),
            ),
            client=ClientConfig(
                id=os.getenv("WHISK_CLIENT_ID", "whisk_client")
            ),
            llm=LLMConfig(
                cloud_api_key=os.getenv("LLAMA_CLOUD_API_KEY")
            ),
            chroma=ChromaConfig(
                path=os.getenv("WHISK_CHROMA_PATH", "chroma_db")
            )
        ) 