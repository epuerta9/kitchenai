from ninja import Schema




class QuerySchema(Schema):
    query: str
    stream: bool = False
    metadata: dict[str, str] | None = None


class QuerySchemaNew(Schema):
    query: str
    stream: bool = False
    metadata: dict[str, str] | None = None


class QueryBaseResponseSchema(Schema):
    input: str | None = None
    output: str | None = None
    retrieval_context: list[str] | None = None
    metadata: dict[str, str] | None = None


class AgentResponseSchema(Schema):
    response: str

class EmbedSchema(Schema):
    text: str
    metadata: dict[str, str] | None = None
