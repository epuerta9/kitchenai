from ninja import Router
from ninja import Schema
from ninja.errors import HttpError
from ninja import Schema
from ..models import EmbedObject

import logging


from django_eventstream import send_event

logger = logging.getLogger(__name__)
router = Router()



class EmbedSchema(Schema):
    text: str
    ingest_label: str | None = None
    metadata: dict[str, str] | None = None

    # Add any other fields from your FileObject model that you want to include
class EmbedObjectResponse(Schema):
    id: int
    text: str
    ingest_label: str
    metadata: dict[str,str]
    status: str

#Embed Object API
@router.post("/", response=EmbedObjectResponse)
async def embed_create(request, data: EmbedSchema):
    """Create a new embed from text"""
    try:
        embed_object = await EmbedObject.objects.acreate(
            text=data.text,
            ingest_label=data.ingest_label,
            metadata=data.metadata if data.metadata else {},
            status=EmbedObject.Status.PENDING,
        )
        return embed_object
    except Exception as e:
        logger.error(f"Unexpected error occurred during embed creation: {e}")
        raise HttpError(500, "Internal Server Error")

@router.get("/{pk}", response=EmbedObjectResponse)
async def embed_get(request, pk: int):
    """Get an embed"""
    try:
        embed_object = await EmbedObject.objects.aget(pk=pk)
        return embed_object
    except EmbedObject.DoesNotExist:
        raise HttpError(404, "Embed not found")
    except Exception as e:
        logger.error(f"Unexpected error occurred while retrieving embed: {e}")
        raise HttpError(500, "Internal Server Error")

@router.get("/", response=list[EmbedObjectResponse])
def embeds_get(request):
    """Get all embeds"""
    try:
        embed_objects = EmbedObject.objects.all()
        return embed_objects
    except Exception as e:
        logger.error(f"Unexpected error occurred while retrieving all embeds: {e}")
        raise HttpError(500, "Internal Server Error")

@router.delete("/{pk}")
async def embed_delete(request, pk: int):
    """Delete an embed"""
    try:
        await EmbedObject.objects.filter(pk=pk).adelete()
        return {"msg": "deleted"}
    except EmbedObject.DoesNotExist:
        raise HttpError(404, "Embed not found")
    except Exception as e:
        logger.error(f"Unexpected error occurred during embed deletion: {e}")
        raise HttpError(500, "Internal Server Error")
