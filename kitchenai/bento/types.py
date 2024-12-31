from enum import Enum, auto

class DependencyType(Enum):
    """Types of dependencies that can be managed."""
    LLM = auto()
    VECTOR_STORE = auto()
    EMBEDDING = auto()  # For future use
    RETRIEVER = auto()  # For future use
    PROMPT = auto()     # For future use 
    MEMORY = auto()     # For future use