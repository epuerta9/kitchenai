from ninja import Schema

class QuerySchema(Schema):
    query: str
    metadata: dict[str, str] | None = None

