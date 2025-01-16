from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from .schema import (
    QuerySchema, 
    StorageSchema, 
    EmbedSchema,
    QueryBaseResponseSchema,
    StorageResponseSchema,
    EmbedResponseSchema,
    BroadcastSchema,
    BroadcastResponseSchema,
    TokenCountSchema,
    SourceNodeSchema
)

# Base message schema
class NatsMessageBase(BaseModel):
    request_id: str
    timestamp: float
    label: str
    client_id: str


class NatsRegisterMessage(BaseModel):
    client_id: str
    ack: bool = False
    message: str = ""

# Request Messages
class QueryRequestMessage(NatsMessageBase, QuerySchema):
    """Schema for query requests"""
    pass

class StorageRequestMessage(NatsMessageBase, StorageSchema):
    """Schema for storage requests"""
    pass

class EmbedRequestMessage(NatsMessageBase, EmbedSchema):
    """Schema for embedding requests"""
    pass

class BroadcastRequestMessage(NatsMessageBase, BroadcastSchema):
    """Schema for broadcast requests"""
    pass

# Response Messages
class QueryResponseMessage(NatsMessageBase, QueryBaseResponseSchema):
    """Schema for query responses"""
    error: Optional[str] = None

class StorageResponseMessage(NatsMessageBase, StorageResponseSchema):
    """Schema for storage responses"""
    error: Optional[str] = None

class EmbedResponseMessage(NatsMessageBase, EmbedResponseSchema):
    """Schema for embedding responses"""
    error: Optional[str] = None

class BroadcastResponseMessage(NatsMessageBase, BroadcastResponseSchema):
    """Schema for broadcast responses"""
    error: Optional[str] = None 