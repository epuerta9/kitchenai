from ninja import Schema

class QuerySchema(Schema):
    query: str
    metadata: dict[str, str] | None = None



class EmbedSchema(Schema):
    text: str
    metadata: dict[str, str] | None = None
