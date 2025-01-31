from ninja.files import UploadedFile
from ninja import Router, File, Form
from kitchenai.core.api.openai.file_types import FileResponse, FilePresignedResponse
import time
import uuid
from ninja import Router, Query
import time
from kitchenai.core.api.openai.file_types import FileListQuery, FileListResponse, FileDeleteResponse
from kitchenai.core.models import FileObject
from ninja.errors import HttpError
import logging
from django.apps import apps
from django.conf import settings
from pydantic import ValidationError
import json
from kitchenai.core.api.openai.file_types import FileRequest
from typing import Dict, Any

logger = logging.getLogger(__name__)
router = Router()

@router.post("", response=FileResponse)
async def upload_file(
    request,
    file: UploadedFile = File(...),
    client_id: str = Form(...),
    namespace: str = Form(...),
    label: str = Form(...),
    version: str | None = Form(None),
    metadata: str | None = Form(""),
):
    """
    Mimics the OpenAI /v1/files endpoint.
    Accepts file and FileRequest fields as form data.
    """
    # Parse metadata string into dict
    metadata_dict = {}
    if metadata:
        try:
            # Split on commas, then on equals signs
            pairs = [pair.split('=') for pair in metadata.split(',') if '=' in pair]
            metadata_dict = {k.strip(): v.strip() for k, v in pairs}
        except Exception as e:
            logger.warning(f"Failed to parse metadata string: {metadata}, error: {e}")

    logger.info(f"Uploading file: {file.name} with metadata: {metadata_dict}")
    try:
        # Create FileRequest from form fields
        file_request = FileRequest(
            client_id=client_id,
            namespace=namespace,
            label=label,
            version=version,
            metadata=metadata_dict
        )        
    except (json.JSONDecodeError, ValidationError) as e:
        raise HttpError(400, f"Invalid purpose format: {str(e)}")

    BentoManager = apps.get_model(settings.KITCHENAI_BENTO_CLIENT_MODEL)
    client_id = file_request.client_id
    try:
        bento_box = await BentoManager.objects.aget(client_id=client_id)
    except BentoManager.DoesNotExist:
        raise HttpError(404, f"Bento box not found for client_id: {client_id}")
    
    label = file_request.label

    # Extract metadata from form
    metadata = file_request.metadata

    if file and label:
        f = await FileObject.objects.acreate(
                file=file,
                name=file.name,
                ingest_label=label,
                metadata=metadata,  # Add metadata to the file object
                bento_box=bento_box,
            )
        
        # Get file size from the file field
        file_size = f.file.size if f.file else 0
        
        # Build the response object
        response_data = {
            "id": str(f.id),
            "bytes": file_size,
            "created_at": int(f.created_at.timestamp()),  # Convert datetime to Unix timestamp
            "filename": f.name,
            "purpose": json.dumps({
                "client_id": f.bento_box.client_id,  # Or extract from metadata
                "namespace": f.bento_box.name,        # Or extract from metadata
                "label": f.ingest_label,
                "version": f.bento_box.version,               # Or extract from metadata
                "metadata": f.metadata or {}
            }),
            "status": f.status,
            "status_details": None
        }
        return response_data




@router.get("", response=FileListResponse)
def list_files(request, query: FileListQuery = Query(...)):
    """
    Mimics GET /v1/files. 
    Returns a list of File objects, possibly filtered by purpose and limited in count.
    """
    try:
        file_objects = FileObject.objects.select_related('bento_box').all()
        
        # Convert FileObject instances to FileResponse objects
        files = [
            FileResponse(
                id=str(f.id),
                bytes=f.file.size,
                created_at=int(f.created_at.timestamp()),
                filename=f.name,
                purpose=json.dumps({
                    "client_id": f.bento_box.client_id,  # Or extract from metadata
                    "namespace": f.bento_box.name,        # Or extract from metadata
                    "label": f.ingest_label,
                    "version": f.bento_box.version,               # Or extract from metadata
                    "metadata": f.metadata or {}
                }),
                status=f.status,
                status_details=None
            )
            for f in file_objects
        ]
        
        return {"data": files, "object": "list"}
        
    except Exception as e:
        logger.error(f"Error in files get: {e}")
        raise HttpError(500, "Error in files get")




@router.delete("/{pk}", response=FileDeleteResponse)
async def delete_file(request, pk: int):
    """
    Mimics DELETE /v1/files/{file_id}.
    In production, you'd remove the file from your storage/db.
    Then return the result with "deleted": True or False.
    """

    """delete a file"""
    try:    
        await FileObject.objects.filter(pk=pk).adelete()
        response_data = {
            "id": str(pk),
            "deleted": True  # or False if something went wrong
        }    
    except FileObject.DoesNotExist:
        raise HttpError(404, "File not found")
    except Exception as e:
        logger.error(f"Error in file delete: {e}")
        raise HttpError(500, "Error in file delete")

    return response_data



@router.get("/{pk}", response=FileResponse)
def get_file(request, pk: int):
    """
    Mimics GET /v1/files/{file_id}.
    Returns a single File object by ID.
    """
    try:
        # Convert string ID to integer and fetch file
        file_object = FileObject.objects.select_related('bento_box').get(id=pk)
        
        # Convert FileObject to FileResponse
        return FileResponse(
            id=str(file_object.id),
            bytes=file_object.file.size,
            created_at=int(file_object.created_at.timestamp()),
            filename=file_object.name,
            purpose=json.dumps({
                "client_id": file_object.bento_box.client_id,
                "namespace": file_object.bento_box.name,
                "label": file_object.ingest_label,
                "version": file_object.bento_box.version,
                "metadata": file_object.metadata or {}
            }),
            status=file_object.status,
            status_details=None,
        )
        
    except FileObject.DoesNotExist:
        raise HttpError(404, f"No file with id: {pk}")
    except Exception as e:
        logger.error(f"Error fetching file {pk}: {e}")
        raise HttpError(500, f"Error fetching file: {e}")
