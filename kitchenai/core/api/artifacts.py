

from ninja import File
from ninja import Router
from ninja import Schema
from ninja.errors import HttpError
from ninja.files import UploadedFile
from ninja import Schema
from ..models import Artifact
import logging


logger = logging.getLogger(__name__)
router = Router()

# Create a Schema that represents FileObject
class ArtifactSchema(Schema):
    name: str
    ingest_label: str | None = None
    metadata: dict[str, str] | None = None
    # Add any other fields from your FileObject model that you want to include
class ArtifactResponse(Schema):
    id: int
    name: str
    ingest_label: str
    metadata: dict[str,str]
    status: str

async def artifact_upload(request, data: ArtifactSchema,file: UploadedFile = File(...)):
    """The artifact object will be created by a python process and the user will only have the id. It will be populated at a later time"""
    try:        
        artifact = await Artifact.objects.acreate(
            name=data.name,
            file=file,
            metadata=data.metadata if data.metadata else {},
            status=Artifact.Status.PENDING
        )
        return artifact
    except Exception as e:
        logger.error(f"Error in artifact upload: {e}")
        raise HttpError(500, "Error in artifact upload")


@router.get("/{pk}", response=ArtifactResponse)
async def artifact_get(request, pk: int):
    """get an artifact"""
    try:
        artifact = await Artifact.objects.aget(pk=pk)
        return artifact
    except Artifact.DoesNotExist:
        raise HttpError(404, "Artifact not found")
    except Exception as e:
        logger.error(f"Error in artifact get: {e}")
        raise HttpError(500, "Error in artifact get")


@router.delete("/{pk}")
async def artifact_delete(request, pk: int):
    """delete an artifact"""
    try:    
        await Artifact.objects.filter(pk=pk).adelete()
        return {"msg": "deleted"}
    except Artifact.DoesNotExist:
        raise HttpError(404, "Artifact not found")
    except Exception as e:
        logger.error(f"Error in artifact delete: {e}")
        raise HttpError(500, "Error in artifact delete")

@router.get("/", response=list[ArtifactResponse])
def artifacts_get(request):
    """get all artifacts"""
    try:
        artifacts = Artifact.objects.all()
        return artifacts
    except Exception as e:
        logger.error(f"Error in artifacts get: {e}")
        raise HttpError(500, "Error in artifacts get")
