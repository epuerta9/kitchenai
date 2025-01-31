import asyncio
import random
from ninja import Router
from kitchenai.core.api.openai.embedding_types import (
    EmbeddingRequest,
    EmbeddingResponse,
    EmbeddingUsage,
    SingleEmbeddingData
)

# Initialize the router for the embeddings endpoint
router = Router()

@router.post("", response=EmbeddingResponse)
async def create_embedding(request, body: EmbeddingRequest):
    """
    Create embeddings for the given input text(s).
    
    This endpoint mimics OpenAI's embeddings API format:
    - Accepts single text or list of texts
    - Returns embeddings in the same format as OpenAI
    - Includes usage statistics
    - Supports different encoding formats
    """
    
    # Extract model name and input texts from request
    model_name = body.model  # e.g., "text-embedding-ada-002"
    
    # Handle both single string and list inputs
    if isinstance(body.input, str):
        texts = [body.input]
    else:
        texts = body.input

    # Create mock embeddings for demonstration
    # In production, you would:
    # 1. Validate the model name
    # 2. Process the texts through your embedding model
    # 3. Track actual token usage
    # 4. Handle any errors appropriately
    embeddings = []
    for i, text in enumerate(texts):
        # Generate random vector (1536 dims matches OpenAI's ada-002)
        fake_vector = [random.random() for _ in range(1536)]
        
        # Create embedding object with proper metadata
        embeddings.append(
            SingleEmbeddingData(
                index=i,
                embedding=fake_vector,
            )
        )

    # Track token usage (mock values for demonstration)
    # In production, calculate actual token counts
    usage_info = EmbeddingUsage(
        prompt_tokens=10,  # Number of tokens in input
        total_tokens=10    # Total tokens processed
    )

    # Construct the final response
    # This matches OpenAI's response format exactly
    response = EmbeddingResponse(
        data=embeddings,      # List of embedding vectors
        model=model_name,     # Model used for embedding
        usage=usage_info      # Token usage statistics
    )
    
    return response
