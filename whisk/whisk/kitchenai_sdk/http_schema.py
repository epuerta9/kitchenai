from pydantic import BaseModel  


"""
Extra body for file requests using the OpenAI API
"""

class FileExtraBody(BaseModel):
    client_id: str
    namespace: str
    label: str
    version: str | None = None
    metadata: str | None = None

class ChatExtraBody(BaseModel):
    namespace: str | None = None
    version: str | None = None
