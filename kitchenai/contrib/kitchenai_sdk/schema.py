from ninja import Schema

class QuerySchema(Schema):
    query: str
    metadata: dict[str, str] | None = None
    stream: bool = False

class QueryResponseSchema(Schema):
    input: str | None = None
    output: str | None = None
    retrieval_context: list[str] | None = None
    metadata: dict[str, str] | None = None
    stream: bool = False
    stream_id: str | None = None


class AgentResponseSchema(Schema):
    response: str

class EmbedSchema(Schema):
    text: str
    metadata: dict[str, str] | None = None
