from ninja import File
from ninja import Router
from ninja import Schema
from ninja.errors import HttpError
from ninja.files import UploadedFile

from .models import FileObject

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

@router.get("/health")
async def default(request):
    return {"msg": "ok"}


@router.post("/file", response=FileObjectResponse)
async def file_upload(request, data: FileObjectSchema,file: UploadedFile = File(...)):
    """main entry for any file upload. Will upload via django storage and emit signals to any listeners"""
    file_object = await FileObject.objects.acreate(
        name=data.name,
        file=file,
        ingest_label=data.ingest_label,
        metadata=data.metadata if data.metadata else {},
        status=FileObject.Status.PENDING
    )
    return file_object


@router.get("/file/{pk}", response=FileObjectResponse)
async def file_get(request, pk: int):
    """get a file"""
    try:
        file_object = await FileObject.objects.aget(pk=pk)
        return file_object
    except FileObject.DoesNotExist:
        raise HttpError(404, "File not found")



@router.delete("/file/{pk}")
async def file_delete(request, pk: int):
    """delete a file"""
    try:
        await FileObject.objects.filter(pk=pk).adelete()
        return {"msg": "deleted"}
    except FileObject.DoesNotExist:
        raise HttpError(404, "File not found")

@router.get("/file", response=list[FileObjectResponse])
def files_get(request):
    """get all files"""
    file_objects = FileObject.objects.all()
    return file_objects
