from ninja import File
from ninja import Router
from ninja import Schema
from ninja.errors import HttpError
from ninja.files import UploadedFile
from ninja import Schema
from .models import FileObject, EmbedObject
from .utils import get_core_kitchenai_app
from django.http import HttpResponse
import posthog
import logging
from django.apps import apps

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



class QuerySchema(Schema):
    query: str
    metadata: dict[str, str] | None = None

class QueryResponseSchema(Schema):
    response: str

class AgentResponseSchema(Schema):
    response: str

class EmbedSchema(Schema):
    text: str
    metadata: dict[str, str] | None = None


@router.post("/agent/{label}", response=AgentResponseSchema)
async def agent(request, label: str, data: QuerySchema):
    """Create a new agent"""
    try:
        posthog.capture("kitchenai_sdk", "agent_handler")
        core_app = apps.get_app_config("core")
        if not core_app.kitchenai_app:
            logger.error("No kitchenai app in core app config")
            return HttpResponse(status=404)
        agent_func = core_app.kitchenai_app._agent_handlers.get(f"{core_app.kitchenai_app._namespace}.{label}")
        if not agent_func:
            logger.error(f"Agent function not found for {label}")
            return HttpResponse(status=404)

        return await agent_func(request, data)
    except Exception as e:      
        logger.error(f"Error in agent: {e}")
        return HttpError(500, "agent function not found")

@router.post("/query/{label}", response=QueryResponseSchema)
async def query(request, label: str, data: QuerySchema):
    """Create a new query"""
    """process file async function for core app using storage task"""
    try:
        core_app = apps.get_app_config("core")
        if not core_app.kitchenai_app:
            logger.error("No kitchenai app in core app config")
            return HttpResponse(status=404)
        
        print(f"core_app.kitchenai_app._query_handlers: {core_app.kitchenai_app._query_handlers}")
        query_func = core_app.kitchenai_app._query_handlers.get(f"{core_app.kitchenai_app._namespace}.{label}")
        if not query_func:
            logger.error(f"Query function not found for {label}")
            return HttpResponse(status=404)
        
        return await query_func(request, data)
    except Exception as e:
        logger.error(f"Error in query: {e}")
        return HttpError(500, "query function not found")


