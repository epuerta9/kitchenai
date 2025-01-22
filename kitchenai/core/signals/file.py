import logging
import asyncio

from django.apps import apps
from django.db.models.signals import post_delete
from django.db.models.signals import post_save
from django.dispatch import receiver
from kitchenai.core.broker import whisk
import uuid
import time
import posthog
from ..models import FileObject

from django.dispatch import Signal
from enum import StrEnum
from django.conf import settings
from whisk.kitchenai_sdk.nats_schema import StorageRequestMessage
from asgiref.sync import async_to_sync

logger = logging.getLogger(__name__)


class StorageSignalSender(StrEnum):
    POST_STORAGE_PROCESS = "post_storage_process"
    PRE_STORAGE_PROCESS = "pre_storage_process"
    POST_STORAGE_DELETE = "post_storage_delete"
    PRE_STORAGE_DELETE = "pre_storage_delete"


storage_signal = Signal()


@receiver(post_save, sender=FileObject)
async def file_object_created(sender, instance, created, **kwargs):
    """
    This signal is triggered when a new FileObject is created.
    This will trigger any listeners with matching labels and run them as async tasks
    """

    if created:
        # Ninja api should have all bolted on routes and a storage tasks
        logger.info(f"<kitchenai_core>: FileObject created: {instance.pk}")
        posthog.capture("file_object", "kitchenai_file_object_created")
        await whisk.store_message(
            StorageRequestMessage(
                id=instance.pk,
                request_id=str(uuid.uuid4()),
                timestamp=time.time(),
                name=instance.name,
                label=instance.ingest_label,
                client_id=instance.bento_box.client_id,
                metadata=instance.metadata,
            )
        )


@receiver(post_delete, sender=FileObject)
def file_object_deleted(sender, instance, **kwargs):
    """delete the file from vector db"""
    logger.info(f"<kitchenai_core>: FileObject deleted: {instance.pk}")
    
    try:
        message = StorageRequestMessage(
            id=instance.pk,
            request_id=str(uuid.uuid4()),
            timestamp=time.time(),
            name=instance.name,
            label=instance.ingest_label,
            client_id=instance.bento_box.client_id,
        )
        
        # Use async_to_sync to properly run and await the async function
        async_to_sync(whisk.store_delete)(message)
        
    except Exception as e:
        logger.error(f"Error deleting file from storage: {e}")
