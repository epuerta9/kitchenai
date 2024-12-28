from ninja import Router
import logging



logger = logging.getLogger(__name__)

router = Router(tags=["playground"])


@router.get("/health")
async def default(request):
    return {"msg": "ok"}

