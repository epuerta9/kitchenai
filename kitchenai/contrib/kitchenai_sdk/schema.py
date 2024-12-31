from ninja import Schema
from typing import Any
from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Dict, Callable




class QuerySchema(Schema):
    query: str
    stream: bool = False
    stream_id: str | None = None
    metadata: dict[str, str] | None = None



class SourceNodeSchema(BaseModel):
    text: str
    metadata: Dict
    score: float

class QueryBaseResponseSchema(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    input: Optional[str] = None
    output: Optional[str] = None
    retrieval_context: Optional[List[SourceNodeSchema]] = None
    generator: Optional[Callable] = None
    metadata: Optional[Dict[str, Any]] = None

    @classmethod
    def from_response(cls, data, response):
        source_nodes = []
        if hasattr(response, 'source_nodes'):
            for node in response.source_nodes:
                source_nodes.append(SourceNodeSchema(
                    text=node.node.text,
                    metadata=node.node.metadata,
                    score=node.score
                ))
        
        return cls(
            input=data.query,
            output=response.response,
            retrieval_context=source_nodes,
            metadata=response.metadata
        )

class StorageSchema(Schema):
    dir: str
    metadata: dict[str, str] | None = None
    extension: str | None = None

class AgentResponseSchema(Schema):
    response: str

class EmbedSchema(Schema):
    text: str
    metadata: dict[str, str] | None = None
