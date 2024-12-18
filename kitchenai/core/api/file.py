

from ninja import File
from ninja import Router
from ninja import Schema
from ninja.errors import HttpError
from ninja.files import UploadedFile
from ninja import Schema
from ..models import FileObject
import logging


logger = logging.getLogger(__name__)
router = Router()

# Create a Schema that represents FileObject
class FileObjectSchema(Schema):
    name: str
    ingest_label: str | None = None
    metadata: dict[str, str] | None = None
    # Add any other fields from your FileObject model that you want to include
class FileObjectResponse(Schema):
    id: int
    name: str
    ingest_label: str
    metadata: dict[str,str]
    status: str

@router.post("/", response=FileObjectResponse)
async def file_upload(request, data: FileObjectSchema,file: UploadedFile = File(...)):
    """main entry for any file upload. Will upload via django storage and emit signals to any listeners"""
    try:        
        file_object = await FileObject.objects.acreate(
            name=data.name,
            file=file,
            ingest_label=data.ingest_label,
            metadata=data.metadata if data.metadata else {},
            status=FileObject.Status.PENDING
        )
        return file_object
    except Exception as e:
        logger.error(f"Error in file upload: {e}")
        raise HttpError(500, "Error in file upload")


@router.get("/{pk}", response=FileObjectResponse)
async def file_get(request, pk: int):
    """get a file"""
    try:
        file_object = await FileObject.objects.aget(pk=pk)
        return file_object
    except FileObject.DoesNotExist:
        raise HttpError(404, "File not found")
    except Exception as e:
        logger.error(f"Error in file get: {e}")
        raise HttpError(500, "Error in file get")


@router.delete("/{pk}")
async def file_delete(request, pk: int):
    """delete a file"""
    try:    
        await FileObject.objects.filter(pk=pk).adelete()
        return {"msg": "deleted"}
    except FileObject.DoesNotExist:
        raise HttpError(404, "File not found")
    except Exception as e:
        logger.error(f"Error in file delete: {e}")
        raise HttpError(500, "Error in file delete")

@router.get("/", response=list[FileObjectResponse])
def files_get(request):
    """get all files"""
    try:
        file_objects = FileObject.objects.all()
        return file_objects
    except Exception as e:
        logger.error(f"Error in files get: {e}")
        raise HttpError(500, "Error in files get")