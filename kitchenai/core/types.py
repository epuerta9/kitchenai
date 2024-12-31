from enum import Enum

class EnvVars(str, Enum):
    MODEL_TYPE = "MODEL_TYPE"
    MODEL_NAME = "MODEL_NAME"
    TEMPERATURE = "TEMPERATURE"
    VECTOR_STORE = "VECTOR_STORE" 
    CHUNK_SIZE = "CHUNK_SIZE"

class ModelType(str, Enum):
    LITELLM = "litellm"
    OLLAMA = "ollama"

class ModelName(str, Enum):
    GPT4O = "gpt-4o"
    GPT4O_MINI = "gpt-4o-mini"
    LLAMA2 = "llama2"
    MISTRAL = "mistral"
    MIXTRAL = "mixtral"

class VectorStore(str, Enum):
    CHROMA = "chroma"

