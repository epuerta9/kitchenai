from enum import Enum

class TestResultReason(str, Enum):
    NO_RETRIEVAL_CONTEXT = "Skipping test - no retrieval context available"

