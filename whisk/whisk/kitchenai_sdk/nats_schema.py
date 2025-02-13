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
    SourceNodeSchema,
    WhiskStorageGetRequestSchema,
    WhiskStorageGetResponseSchema
)

# Base message schema
class NatsMessageBase(BaseModel):
    request_id: str
    timestamp: float
    label: str
    client_id: str
    # namespace: str
    # version: str | None = None

class BentoBox(BaseModel):
    """Schema for bento box configuration"""
    namespace: str
    query_handlers: List[str]
    storage_handlers: List[str]
    embed_handlers: List[str]
    agent_handlers: List[str]

class NatsRegisterMessage(BaseModel):
    """Message for registering a client with KitchenAI"""
    client_id: str
    version: str
    name: str
    bento_box: BentoBox
    client_type: str = "bento_box"
    client_description: str = "Bento box"

# Request Messages
class QueryRequestMessage(NatsMessageBase, WhiskQuerySchema):
    """Schema for query requests"""
    pass

class StorageRequestMessage(NatsMessageBase, WhiskStorageSchema):
    """Schema for storage requests"""
    pass

class StorageGetRequestMessage(NatsMessageBase, WhiskStorageGetRequestSchema):
    """Schema for storage get requests"""
    pass


class EmbedRequestMessage(NatsMessageBase, WhiskEmbedSchema):
    """Schema for embedding requests"""
    id: int

class BroadcastRequestMessage(NatsMessageBase, WhiskBroadcastSchema):
    """Schema for broadcast requests"""
    pass

# Response Messages

class StorageGetResponseMessage(NatsMessageBase, WhiskStorageGetResponseSchema):
    """Schema for storage get responses"""
    pass

class QueryResponseMessage(NatsMessageBase, WhiskQueryBaseResponseSchema):
    """Schema for query responses"""
    error: Optional[str] = None


class RegisterResponseMessage(NatsMessageBase, NatsRegisterMessage):
    """Schema for register responses"""
    error: Optional[str] = None

class StorageResponseMessage(NatsMessageBase, WhiskStorageResponseSchema):
    """Schema for storage responses"""
    error: Optional[str] = None

class EmbedResponseMessage(NatsMessageBase, WhiskEmbedResponseSchema):
    """Schema for embedding responses"""
    id: int
    error: Optional[str] = None

class BroadcastResponseMessage(NatsMessageBase, WhiskBroadcastResponseSchema):
    """Schema for broadcast responses"""
    error: Optional[str] = None 