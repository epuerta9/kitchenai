from pydantic import BaseModel, Field, constr
from typing import List, Optional, Dict, Any, Annotated
from django.core.exceptions import ImproperlyConfigured

class BentoConfigSchema(BaseModel):
    """Base configuration model for all Bento packages"""
    name: Annotated[str, constr(pattern=r"^[a-zA-Z0-9_-]+$")] = Field(
        ...,
        description="The name identifier of the package"
    )
    description: str = Field(
        ...,
        description="A brief description of the package's purpose"
    )
    namespace: Annotated[str, constr(pattern=r"^[a-zA-Z0-9_-]+$")] = Field(
        ...,
        description="The namespace used for URL routing"
    )
    home: Annotated[str, constr(pattern=r"^[a-zA-Z0-9_-]+$")] = Field(
        ...,
        description="The home route identifier"
    )
    tags: List[Annotated[str, constr(pattern=r"^[a-zA-Z0-9_-]+$")]] = Field(
        ...,
        description="List of tags associated with the package",
        min_items=1
    )
    version: str = Field(
        ...,
        description="The version of the package"
    )
    settings: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional settings specific to this bento"
    )

    class Config:
        extra = "forbid"


def validate_bento_config(config: dict) -> BentoConfigSchema:
    """
    Validates the bento configuration against the base schema.
    
    Args:
        config (dict): The configuration dictionary to validate
        
    Returns:
        BaseBentoConfig: The validated configuration object
        
    Raises:
        ImproperlyConfigured: If the configuration is invalid
    """
    try:
        return BentoConfigSchema(**config)
    except Exception as e:
        raise ImproperlyConfigured(f"Invalid bento configuration: {str(e)}")

