from typing import List, Union, Optional
from pydantic import BaseModel, Field

#
# Request Models
#

class EmbeddingRequest(BaseModel):
    model: str = Field(..., description="ID of the model to use for generating embeddings.")
    input: Union[str, List[str]] = Field(
        ...,
        description=(
            "The input text(s) to embed. Can be a single string or a list of strings. "
            "Each string must not exceed the model's max tokens limit."
        )
    )
    encoding_format: Optional[str] = Field(
        "float",
        description="How to encode the embedding. 'float' or 'base64'. Default 'float'."
    )
    dimensions: Optional[int] = Field(
        None,
        description="Number of dimensions for the embedding (if supported)."
    )
    user: Optional[str] = Field(
        None,
        description="Unique identifier representing your end-user."
    )

#
# Response Models
#


class EmbeddingUsage(BaseModel):
    """Tracks token usage (optional)."""
    prompt_tokens: int
    total_tokens: int


class SingleEmbeddingData(BaseModel):
    """
    Represents a single embedding vector in the response.
    Each embedding object includes:
      - index
      - embedding (list of floats)
      - object == "embedding"
    """
    object: str = Field("embedding", description="Always 'embedding'.")
    index: int = Field(..., description="Index of this embedding in the returned list.")
    embedding: List[float] = Field(
        ...,
        description="The actual embedding vector, a list of floats."
    )

class EmbeddingUsage(BaseModel):
    """
    Optional usage stats you may want to include, 
    similar to OpenAI's usage fields (prompt_tokens, etc.).
    """
    prompt_tokens: int
    total_tokens: int

class EmbeddingResponse(BaseModel):
    """
    The top-level response shape for /v1/embeddings:
      - object = "list"
      - data = list of SingleEmbeddingData
      - model = name of the model used
      - usage = optional usage stats
    """
    object: str = Field("list", description="Typically 'list'.")
    data: List[SingleEmbeddingData] = Field(
        ...,
        description="Array of embedding objects."
    )
    model: str = Field(
        ...,
        description="The model used to generate embeddings."
    )
    usage: Optional[EmbeddingUsage] = None
