from ninja import File
from ninja import Router
from ninja import Schema
from ninja.errors import HttpError
from ninja.files import UploadedFile

from .models import FileObject, EmbedObject
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
@router.post("/embed", response=EmbedObjectResponse)
async def embed_create(request, data: EmbedSchema):
    """Create a new embed from text"""
    embed_object = await EmbedObject.objects.acreate(
        text=data.text,
        ingest_label=data.ingest_label,
        metadata=data.metadata if data.metadata else {},
        status=EmbedObject.Status.PENDING,
    )
    return embed_object

@router.get("/embed/{pk}", response=EmbedObjectResponse)
async def embed_get(request, pk: int):
    """Get an embed"""
    try:
        embed_object = await EmbedObject.objects.aget(
            pk=pk,
        )
        return embed_object
    except EmbedObject.DoesNotExist:
        raise HttpError(404, "Embed not found")
    
@router.get("/embed", response=list[EmbedObjectResponse])
def embeds_get(request):
    """Get all embeds"""
    embed_objects = EmbedObject.objects.all()
    return embed_objects    

@router.delete("/embed/{pk}")
async def embed_delete(request, pk: int):
    """Delete an embed"""
    try:
        await EmbedObject.objects.filter(pk=pk).adelete()
        return {"msg": "deleted"}
    except EmbedObject.DoesNotExist:
        raise HttpError(404, "Embed not found")
