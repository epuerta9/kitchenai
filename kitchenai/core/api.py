import asyncio

from ninja import Router, Schema, File
from ninja.files import UploadedFile
from .models import FileObject
from typing import Optional, Dict
from ninja.errors import HttpError

router = Router()

# Create a Schema that represents FileObject
class FileObjectSchema(Schema):
    name: str
    ingest_label: Optional[str] = None
    metadata: Optional[Dict[str,str]] = None
    # Add any other fields from your FileObject model that you want to include
class FileObjectResponse(Schema):
    id: int
    name: str
    ingest_label: str
    metadata: Dict[str,str]
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
    try:
        file_object = await FileObject.objects.aget(pk=pk)
        return file_object
    except FileObject.DoesNotExist:
        raise HttpError(404, "File not found")
