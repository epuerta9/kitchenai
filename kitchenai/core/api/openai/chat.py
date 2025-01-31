from ninja import Router, Form
from pydantic import BaseModel
from ninja.errors import HttpError
import logging
from django.apps import apps
from kitchenai.core.signals import query_signal, QuerySignalSender
from django_eventstream import send_event
from kitchenai.core.exceptions import QueryHandlerBadRequestError
from kitchenai.core.broker import whisk


import time
import uuid
import re
import json

from whisk.kitchenai_sdk.nats_schema import QueryRequestMessage, QueryResponseMessage

from kitchenai.core.api.openai.chat_types import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatCompletionChunk,
    ChatStreamChoice,
    ChatStreamChoiceDelta,
    ChatCompletionUsage,
)

import datetime
import asyncio
from kitchenai.exceptions import NoRespondersError
from pydantic import ValidationError

logger = logging.getLogger(__name__)
router = Router()
from django.http import StreamingHttpResponse
import re



@router.post("/completions", response=ChatCompletionResponse)
async def oachat(
    request,
    body: ChatCompletionRequest,
):
    """
    Chat Completion endpoint that handles both streaming and non-streaming requests.
    """
    # Get raw request data to access all fields
    raw_data = json.loads(request.body)

    # Parse model field which comes in format '@clientid/label'
    if not body.model.startswith('@'):
        raise HttpError(400, "Model must be in format '@clientid/label'")
    
    try:
        client_id, label = body.model[1:].split('/')  # Remove @ and split

    except ValueError:
        raise HttpError(400, "Invalid model format. Must be '@clientid/label'")
    
    # Update body model with fields from raw data
    body.namespace = raw_data.get('namespace')
    body.version = raw_data.get('version')
    
    # Validate the model after updating
    try:
        body.model_validate(body.model_dump())  # This will raise ValidationError if required fields are missing
    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        raise HttpError(422, f"Invalid request: {e}")
    
    
    if body.stream:
        # Typically, you'd parse the request body or query to figure out what to generate.
        # For this example, we'll just do a small "fake" streaming of partial tokens.
        raise NotImplementedError("Streaming is not implemented yet")
        # async def sse_stream():
        #     # 1) Prepare overall info for the chunk responses
        #     completion_id = "chatcmpl-abc123"
        #     model_name = "gpt-4"
        #     timestamp = int(datetime.now().timestamp())

        #     # 2) Mock partial tokens
        #     partial_tokens = ["Hello", " ", "world", "!"]

        #     # 3) Stream partial chunks
        #     for i, token in enumerate(partial_tokens):
        #         # Create a chunk model
        #         chunk_obj = ChatCompletionChunk(
        #             id=completion_id,
        #             object="chat.completion.chunk",
        #             created=timestamp,
        #             model=model_name,
        #             choices=[
        #                 ChatStreamChoice(
        #                     index=0,
        #                     delta=ChatStreamChoiceDelta(
        #                         # We only send 'content' as partial updates
        #                         content=token
        #                     ),
        #                     finish_reason=None,  # not finished yet
        #                 )
        #             ],
        #             # usage is usually None for intermediate chunks
        #             usage=None,
        #         )

        #         # Convert to JSON, yield as SSE
        #         data_str = chunk_obj.model_dump_json()
        #         yield f"data: {data_str}\n\n"

        #         # Sleep a tiny bit to simulate streaming time
        #         await asyncio.sleep(0.5)

        #     # 4) Final chunk to signal "finish" with finish_reason
        #     final_chunk = ChatCompletionChunk(
        #         id=completion_id,
        #         object="chat.completion.chunk",
        #         created=timestamp,
        #         model=model_name,
        #         choices=[
        #             ChatStreamChoice(
        #                 index=0, delta=ChatStreamChoiceDelta(), finish_reason="stop"
        #             )
        #         ],
        #         usage=ChatCompletionUsage(
        #             prompt_tokens=5, completion_tokens=4, total_tokens=9
        #         ),
        #     )
        #     yield f"data: {final_chunk.model_dump_json()}\n\n"

        #     # 5) Finally, send the sentinel [DONE]
        #     yield "data: [DONE]\n\n"

        # # Return a StreamingHttpResponse with text/event-stream
        # response = StreamingHttpResponse(
        #     sse_stream(),
        #     content_type="text/event-stream",
        # )
        # # SSE typically needs no-cache and unbuffered
        # response["Cache-Control"] = "no-cache"
        # response["X-Accel-Buffering"] = "no"
        # return response
    metadata = body.metadata

    # Create message for whisk
    message = QueryRequestMessage(
        request_id=str(uuid.uuid4()),
        timestamp=time.time(),
        query=body.messages[-1].content,  # Get the last message content
        metadata=metadata,
        messages=body.messages,
        stream=body.stream,
        label=label,  # or appropriate label for chat completions
        client_id=client_id,  # or appropriate client ID
    )
    try:
        response = await whisk.query(message)
    except Exception as e:
        if "no responders available for request" in str(e).lower():
            logger.error("No NATS responders available")
            raise NoRespondersError(
                message="No chat completion service available",
                details={"client_id": message.client_id, "label": message.label},
            )
        logger.error(f"Error in chat completion: {str(e)}")
        raise HttpError(500, "Error processing chat completion request")

    response_data = QueryResponseMessage(**response.decoded_body)
    logger.info(f"Response data: {response_data}")
    # Add default empty dict for response_data if None
    if response_data.error:
        if "No task found for query" in response_data.error:
            # Return ChatCompletionResponse with error details
            return ChatCompletionResponse(
                id=response_data.request_id,
                created=int(time.time()),
                model=body.model,
                choices=[
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": "No matching task found for the given query.",
                        },
                        "finish_reason": "error",
                        "error": "No matching task found for the given query. Please verify the model name and try again.",
                        
                    }
                ],
                usage=None
            )
        else:
            # Handle other errors similarly
            return ChatCompletionResponse(
                id=response_data.request_id,
                created=int(time.time()),
                model=body.model,
                choices=[
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": f"Error: {response_data.error}",
                        },
                        "finish_reason": "error",
                        "error": f"Error processing chat completion request: {response_data.error}",
                    }
                ],
                usage=None
            )
    
    # Get metadata with default empty dict
    metadata = response_data.metadata
    # Get token_counts with default empty dict
    if metadata:
        token_counts = metadata.get("token_counts", {})
    else:
        token_counts = {}
    
    # Only create usage if metadata exists
    usage = None
    if metadata:
        if token_counts:  # Only create usage if we have token counts
            usage = ChatCompletionUsage(
                prompt_tokens=token_counts.get("llm_prompt_tokens", 0),
                completion_tokens=token_counts.get("llm_completion_tokens", 0),
                total_tokens=token_counts.get("total_llm_tokens", 0),
            )

    retrieval_context = response_data.retrieval_context
    # Construct chat completion response
    return ChatCompletionResponse(
        id=response_data.request_id,
        created=int(time.time()),
        model=body.model,
        choices=[
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": response_data.output,
                    "retrieval_context": retrieval_context
                },
                "finish_reason": "stop",
            }
        ],
        usage=usage
    )
