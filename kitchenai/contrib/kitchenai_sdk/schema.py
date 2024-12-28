from ninja import Schema
from typing import Any




class QuerySchema(Schema):
    query: str
    stream: bool = False
    stream_id: str | None = None
    metadata: dict[str, str] | None = None



class QueryBaseResponseSchema(Schema):
    input: str | None = None
    output: str | None = None
    retrieval_context: list[str] | None = None
    stream_gen: Any | None = None
    metadata: dict[str, str] | None = None


class StorageSchema(Schema):
    dir: str
    metadata: dict[str, str] | None = None
    extension: str | None = None

class AgentResponseSchema(Schema):
    response: str

class EmbedSchema(Schema):
    text: str
    metadata: dict[str, str] | None = None
