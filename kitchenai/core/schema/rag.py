from typing import Literal, Union
from pydantic import BaseModel, Field, field_validator
from kitchenai.core.types import ModelType, ModelName, VectorStore

class RAGConfigSchema(BaseModel):
    llm_type: Union[str, ModelType] = Field(
        default=ModelType.LITELLM,
        description="The type of model to use"
    )
    llm_name: Union[str, ModelName] = Field(
        default=ModelName.GPT4O,
        description="The specific model to use"
    )
    temperature: float = Field(
        default=0.7,
        description="Temperature for model responses",
        ge=0.0,
        le=1.0
    )
    vector_store: Union[str, VectorStore] = Field(
        default=VectorStore.CHROMA,
        description="Vector store backend to use"
    )
    vector_store_endpoint: str = Field(
        default="db",
        description="Endpoint URL for the vector store service"
    )
    chunk_size: int = Field(
        default=1024,
        description="Size of text chunks for processing",
        gt=0
    )

    @field_validator("llm_type")
    def validate_model_type(cls, v):
        if isinstance(v, ModelType):
            return v.value
        if v not in [m.value for m in ModelType]:
            raise ValueError(f"Invalid model type. Must be one of: {[m.value for m in ModelType]}")
        return v

    @field_validator("llm_name")
    def validate_model_name(cls, v, values):
        if isinstance(v, ModelName):
            v = v.value
        allowed_models = {
            "litellm": [ModelName.GPT4O.value, ModelName.GPT4O_MINI.value],
            "ollama": [ModelName.LLAMA2.value, ModelName.MISTRAL.value, ModelName.MIXTRAL.value]
        }
        model_type = values.data.get("model_type", ModelType.LITELLM.value)
        if v not in allowed_models[model_type]:
            raise ValueError(f"Model {v} not allowed for {model_type}. Allowed models: {allowed_models[model_type]}")
        return v

    @field_validator("vector_store")
    def validate_vector_store(cls, v):
        if isinstance(v, VectorStore):
            return v.value
        if v not in [vs.value for vs in VectorStore]:
            raise ValueError(f"Invalid vector store. Must be one of: {[vs.value for vs in VectorStore]}")
        return v