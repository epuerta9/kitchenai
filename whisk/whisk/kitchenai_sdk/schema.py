from pydantic import BaseModel, ConfigDict, computed_field
from typing import List, Optional, Dict, Any, Callable
from enum import StrEnum, auto


class TokenCountSchema(BaseModel):
    embedding_tokens: Optional[int] = None
    llm_prompt_tokens: Optional[int] = None 
    llm_completion_tokens: Optional[int] = None
    total_llm_tokens: Optional[int] = None


class QuerySchema(BaseModel):
    query: str
    stream: bool = False
    stream_id: Optional[str] = None
    metadata: Optional[Dict[str, str]] = None



class SourceNodeSchema(BaseModel):
    text: str
    metadata: Dict
    score: float

class QueryBaseResponseSchema(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    input: Optional[str] = None
    output: Optional[str] = None
    retrieval_context: Optional[List[SourceNodeSchema]] = None
    stream_gen: Any | None = None
    metadata: Optional[Dict[str, Any]] = None
    token_counts: Optional[TokenCountSchema] = None

    @classmethod
    def from_response(cls, data, response, metadata=None, token_counts: TokenCountSchema | None = None):
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
    def from_response_stream(cls, data, response, stream_gen, metadata: dict[str, Any] | None = {}, token_counts: TokenCountSchema | None = None):
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

class StorageSchema(BaseModel):
    dir: str
    metadata: Optional[Dict[str, str]] = None
    extension: Optional[str] = None

class StorageResponseSchema(BaseModel):
    metadata: Optional[Dict[str, Any]] = None
    token_counts: Optional[TokenCountSchema] = None

    @classmethod
    def with_token_counts(cls, token_counts: TokenCountSchema):
        return cls(token_counts=token_counts)

class AgentResponseSchema(BaseModel):  
    response: str

class EmbedSchema(BaseModel):
    text: str
    metadata: Optional[Dict[str, str]] = None

class EmbedResponseSchema(BaseModel):
    metadata: Optional[Dict[str, Any]] = None
    token_counts: Optional[TokenCountSchema] = None

    @classmethod
    def with_token_counts(cls, token_counts: TokenCountSchema):
        return cls(token_counts=token_counts)

class BroadcastSchema(BaseModel):
    """Schema for broadcast messages"""
    message: str
    type: str = "info"  # info, warning, error, etc.
    metadata: Optional[Dict[str, Any]] = None

class BroadcastResponseSchema(BaseModel):
    """Schema for broadcast responses"""
    message: str
    type: str
    metadata: Optional[Dict[str, Any]] = None
    token_counts: Optional[TokenCountSchema] = None

    @classmethod
    def from_broadcast(cls, broadcast: BroadcastSchema, token_counts: TokenCountSchema | None = None):
        return cls(
            message=broadcast.message,
            type=broadcast.type,
            metadata=broadcast.metadata,
            token_counts=token_counts
        )

class DependencyType(StrEnum):
    """Types of dependencies that can be managed."""
    LLM = auto()
    VECTOR_STORE = auto()
    EMBEDDING = auto()  # For future use
    RETRIEVER = auto()  # For future use
    PROMPT = auto()     # For future use 
    MEMORY = auto()     # For future use