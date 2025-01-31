from typing import Optional
from pydantic import BaseModel, Field

class ModelObject(BaseModel):
    """
    Represents a single model object in OpenAI style.
    For the /v1/models endpoint, each item in the data array.
    """
    id: str = Field(..., description="Unique identifier for the model.")
    object: str = Field("model", description="Always 'model' for a model object.")
    created: Optional[int] = Field(None, description="Unix timestamp (in seconds) when the model was created.")
    owned_by: Optional[str] = Field(None, description="Organization or user that owns the model.")
    # You can include more fields if your system needs them.
    # Some references add e.g. permissions, root, parent, etc.


class ModelsListResponse(BaseModel):
    """
    The top-level response for GET /v1/models:
    - object='list'
    - data=[ModelObject, ...]
    """
    object: str = Field("list", description="Always 'list' for a list of models.")
    data: list[ModelObject] = Field(..., description="An array of model objects.")
