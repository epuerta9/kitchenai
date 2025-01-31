from pydantic import BaseModel, ConfigDict, computed_field
from typing import List, Optional, Dict, Any, Callable
from enum import StrEnum, auto


class TokenCountSchema(BaseModel):
    embedding_tokens: Optional[int] = None
    llm_prompt_tokens: Optional[int] = None 
    llm_completion_tokens: Optional[int] = None
    total_llm_tokens: Optional[int] = None


class WhiskQuerySchema(BaseModel):
    query: str
    stream: bool = False
    stream_id: Optional[str] = None
    metadata: Optional[Dict[str, str]] = None
    label: Optional[str]

    # OpenAI Chat Completion Schema as optional for more context. Will come is as a dict.
    messages: Optional[List[object]] = None



class SourceNodeSchema(BaseModel):
    text: str
    metadata: Dict
    score: float

class WhiskQueryBaseResponseSchema(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    input: Optional[str] = None
    output: Optional[str] = None
    retrieval_context: Optional[List[SourceNodeSchema]] = None
    stream_gen: Any | None = None
    metadata: Optional[Dict[str, Any]] = {}
    token_counts: Optional[TokenCountSchema] = None


    # OpenAI Chat Completion Schema as optional for more context. Will come is as a dict.
    messages: Optional[List[object]] = None
    
    @classmethod
    def from_llama_response(cls, data, response, metadata=None, token_counts: TokenCountSchema | None = None):
        source_nodes = []
        if hasattr(response, 'source_nodes'):
            for node in response.source_nodes:
                source_nodes.append(SourceNodeSchema(
                    text=node.node.text,
                    metadata=node.node.metadata,
                    score=node.score
                ))
        if metadata and response.metadata:
            response.metadata.update(metadata)
        return cls(
            input=data.query,
            output=response.response,
            retrieval_context=source_nodes,
            metadata=response.metadata,
            token_counts=token_counts
        )
    
    @classmethod
    def from_llama_response_stream(cls, data, response, stream_gen, metadata: dict[str, Any] | None = {}, token_counts: TokenCountSchema | None = None):
        source_nodes = []
        if hasattr(response, 'source_nodes'):
            for node in response.source_nodes:
                source_nodes.append(SourceNodeSchema(
                    text=node.node.text,
                    metadata=node.node.metadata,
                    score=node.score
                ))

        if metadata:
            response.metadata.update(metadata)
        return cls(
            input=data.query,
            retrieval_context=source_nodes,
            metadata=response.metadata,
            stream_gen=stream_gen,
            token_counts=token_counts
        )
    
    @classmethod
    def with_string_retrieval_context(cls, data, response: str, retrieval_context: List[str], metadata: dict[str, Any] | None = {}, token_counts: TokenCountSchema | None = None):
        return cls(
            input=data.query,
            output=response.response,
            retrieval_context=[SourceNodeSchema(text=context, metadata=metadata, score=1.0) for context in retrieval_context],
            metadata=response.metadata,
            token_counts=token_counts
        )
    
    @classmethod
    def from_llm_invoke(cls, input: str, output: str, metadata=None, token_counts: TokenCountSchema | None = None):        
        return cls(
            input=input,
            output=output,
            metadata=metadata,
            token_counts=token_counts
        )

class WhiskStorageStatus(StrEnum):
    PENDING = "pending"
    ERROR = "error"
    COMPLETE = "complete"
    ACK = "ack"

class WhiskStorageSchema(BaseModel):
    id: int
    name: str
    label: str 
    data: Optional[bytes] = bytes()
    metadata: Optional[Dict[str, str]] = None
    extension: Optional[str] = None

class WhiskStorageGetRequestSchema(BaseModel):
    id: int
    presigned: bool = False


class WhiskStorageGetResponseSchema(BaseModel):
    presigned_url: Optional[str] = None
    error: Optional[str] = None

class WhiskStorageResponseSchema(BaseModel):
    id: int
    status: WhiskStorageStatus = WhiskStorageStatus.PENDING
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    token_counts: Optional[TokenCountSchema] = None

    @classmethod
    def with_token_counts(cls, token_counts: TokenCountSchema):
        return cls(token_counts=token_counts)

class WhiskAgentResponseSchema(BaseModel):  
    response: str

class WhiskEmbedSchema(BaseModel):
    label: str
    text: Optional[str] = None
    metadata: Optional[Dict[str, str]] = None

class WhiskEmbedResponseSchema(BaseModel):
    metadata: Optional[Dict[str, Any]] = None
    token_counts: Optional[TokenCountSchema] = None

    @classmethod
    def with_token_counts(cls, token_counts: TokenCountSchema):
        return cls(token_counts=token_counts)

class WhiskBroadcastSchema(BaseModel):
    """Schema for broadcast messages"""
    message: str
    type: str = "info"  # info, warning, error, etc.
    metadata: Optional[Dict[str, Any]] = None

class WhiskBroadcastResponseSchema(BaseModel):
    """Schema for broadcast responses"""
    message: str
    type: str
    metadata: Optional[Dict[str, Any]] = None
    token_counts: Optional[TokenCountSchema] = None

    @classmethod
    def from_broadcast(cls, broadcast: WhiskBroadcastSchema, token_counts: TokenCountSchema | None = None):
        return cls(
            message=broadcast.message,
            type=broadcast.type,
            metadata=broadcast.metadata,
            token_counts=token_counts
        )


class NatsMessageMetadata(BaseModel):
    content_type: str
    correlation_id: str
    reply_to: Optional[str] = None
    message_id: str

class NatsMessage(BaseModel):
    """
    Used for Request/Response messages
    """
    body: bytes
    headers: Dict[str, str]
    metadata: NatsMessageMetadata
    decoded_body: Dict[str, Any]

    @classmethod
    def from_faststream(cls, msg):
        return cls(
            body=msg.body,
            headers=msg.headers,
            metadata=NatsMessageMetadata(
                content_type=msg.content_type,
                correlation_id=msg.correlation_id,
                reply_to=msg.reply_to,
                message_id=msg.message_id,
                request_id=msg._decoded_body.get('request_id'),
            subject=msg.raw_message.subject,
            client_id=msg._decoded_body.get('client_id')
            ),
            decoded_body=msg._decoded_body
        )

class DependencyType(StrEnum):
    """Types of dependencies that can be managed."""
    LLM = auto()
    VECTOR_STORE = auto()
    EMBEDDING = auto()  # For future use
    RETRIEVER = auto()  # For future use
    PROMPT = auto()     # For future use 
    MEMORY = auto()     # For future use