from ninja import Router
import time

from kitchenai.core.api.openai.model_types import ModelsListResponse, ModelObject

router = Router()

@router.get("/models", response=ModelsListResponse)
def list_models(request):
    """
    Mimics GET /v1/models. 
    Returns a list of model objects with minimal info.
    """

    # Example mock data:
    model_list = [
        ModelObject(
            id="model-id-0",
            created=int(time.time()) - 100,
            owned_by="organization-owner"
        ),
        ModelObject(
            id="model-id-1",
            created=int(time.time()) - 50,
            owned_by="organization-owner"
        ),
        ModelObject(
            id="model-id-2",
            created=int(time.time()),
            owned_by="openai"
        ),
    ]

    response_data = ModelsListResponse(
        data=model_list
    )
    return response_data
