from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from .schema import (
    WhiskQuerySchema,
    WhiskStorageSchema,
    WhiskEmbedSchema,
    WhiskQueryBaseResponseSchema,
    WhiskStorageResponseSchema,
    WhiskEmbedResponseSchema,
    WhiskBroadcastSchema,
    WhiskBroadcastResponseSchema,
    TokenCountSchema,
    SourceNodeSchema
)

# Base message schema
class NatsMessageBase(BaseModel):
    request_id: str
    timestamp: float
    label: str
    client_id: str

class BentoBox(BaseModel):
    namespace: str
    query_handlers: list[str]
    storage_handlers: list[str]
    embed_handlers: list[str]
    agent_handlers: list[str]
    

class NatsRegisterMessage(BaseModel):
    name: str
    client_id: str
    client_description: str | None = None
    client_type: str = "bento"
    ack: bool = False
    message: str = ""
    bento_box: BentoBox | None = None
    error: str | None = None
    version: str

# Request Messages
class QueryRequestMessage(NatsMessageBase, WhiskQuerySchema):
    """Schema for query requests"""
    pass

class StorageRequestMessage(NatsMessageBase, WhiskStorageSchema):
    """Schema for storage requests"""
    pass

class EmbedRequestMessage(NatsMessageBase, WhiskEmbedSchema):
    """Schema for embedding requests"""
    pass

class BroadcastRequestMessage(NatsMessageBase, WhiskBroadcastSchema):
    """Schema for broadcast requests"""
    pass

# Response Messages
class QueryResponseMessage(NatsMessageBase, WhiskQueryBaseResponseSchema):
    """Schema for query responses"""
    error: Optional[str] = None

class StorageResponseMessage(NatsMessageBase, WhiskStorageResponseSchema):
    """Schema for storage responses"""
    error: Optional[str] = None

class EmbedResponseMessage(NatsMessageBase, WhiskEmbedResponseSchema):
    """Schema for embedding responses"""
    error: Optional[str] = None

class BroadcastResponseMessage(NatsMessageBase, WhiskBroadcastResponseSchema):
    """Schema for broadcast responses"""
    error: Optional[str] = None 