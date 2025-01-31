from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from ninja import Schema

class FilePresignedResponse(Schema):
    id: int
    name: str
    ingest_label: str
    metadata: dict[str,str]
    status: str
    presigned_url: str | None = None

class FileResponse(BaseModel):
    """
    Represents the file object returned after uploading or retrieving
    a file in the style of the OpenAI /v1/files endpoint.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)  # Allow UploadedFile type
    
    id: str = Field(..., description="The file identifier.")
    object: str = Field("file", description="Always 'file'.")
    bytes: int = Field(..., description="The size of the file in bytes.")
    created_at: int = Field(..., description="Unix timestamp (in seconds) of when the file was created.")
    filename: str = Field(..., description="The name of the file.")
    purpose: str = Field(..., description="Intended purpose of the file. E.g. 'assistants', 'fine-tune'.")
    
    # Deprecated fields, still shown for completeness
    status: Optional[str] = Field(None, description="(Deprecated) The status of the file, e.g. 'uploaded'.")
    status_details: Optional[str] = Field(None, description="(Deprecated) Additional details for file status.")


# file_list_response.py


class FileRequest(Schema):
    client_id: str
    namespace: str
    label: str
    version: str | None = None
    metadata: dict[str, str] | None = {}

class FileListResponse(BaseModel):
    """
    The top-level response for GET /v1/files:
    - object = 'list'
    - data = list of FileResponse
    Possibly includes pagination or other fields if needed.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    object: str = Field("list", description="Always 'list' for a list of files.")
    data: List[FileResponse]


# file_list_query.py

class FileListQuery(BaseModel):
    """
    Query parameters for GET /v1/files
    """
    purpose: Optional[str] = Field(None, description="Only return files with the given purpose.")
    limit: Optional[int] = Field(10000, description="Max number of files to return (1-10000).")
    order: Optional[str] = Field("desc", description="Sort order by created_at (asc or desc).")
    after: Optional[str] = Field(None, description="A cursor for pagination, e.g. an object ID.")


# file_delete_response.py
class FileDeleteResponse(BaseModel):
    """
    Represents the response after deleting a file. 
    Example:
    {
      "id": "file-abc123",
      "object": "file",
      "deleted": true
    }
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    id: str = Field(..., description="The file identifier.")
    object: str = Field("file", description="Always 'file'.")
    deleted: bool = Field(..., description="Indicates if the file was deleted successfully.")
