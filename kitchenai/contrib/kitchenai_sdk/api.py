from ninja import Schema

class QuerySchema(Schema):
    query: str
    metadata: dict[str, str] | None = None

class QueryResponseSchema(Schema):
    response: str

class AgentResponseSchema(Schema):
    response: str

class EmbedSchema(Schema):
    text: str
    metadata: dict[str, str] | None = None
