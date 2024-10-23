import logging

from ninja import NinjaAPI

logger = logging.getLogger(__name__)

api = NinjaAPI()


@api.get("/health")
async def default(request):

    return {"msg":"ok"}
