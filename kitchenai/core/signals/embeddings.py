import logging

from django.apps import apps
from django.db.models.signals import post_delete
from django.db.models.signals import post_save
from django.dispatch import receiver
import posthog
from ..models import EmbedObject
from django.dispatch import Signal
from kitchenai.core.broker import whisk
from whisk.kitchenai_sdk.nats_schema import EmbedRequestMessage

logger = logging.getLogger(__name__)
from django.conf import settings
import uuid
import time

embed_signal = Signal()
from enum import StrEnum


class EmbedSignalSender(StrEnum):
    POST_EMBED_PROCESS = "post_embed_process"
    PRE_EMBED_PROCESS = "pre_embed_process"
    POST_EMBED_DELETE = "post_embed_delete"
    PRE_EMBED_DELETE = "pre_embed_delete"


@receiver(post_save, sender=EmbedObject)
async def embed_object_created(sender, instance, created, **kwargs):
    """
    This signal is triggered when a new EmbedObject is created.
    This will trigger any listeners with matching labels and run them as async tasks
    """
    if created:
        logger.info(f"<kitchenai_core>: EmbedObject created: {instance.pk}")
        posthog.capture("embed_object", "kitchenai_embed_object_created")
        await whisk.embed(
            EmbedRequestMessage(
                id=instance.id,
                label=instance.ingest_label,
                text=instance.text,
                client_id=instance.bento_box.client_id,
                request_id=str(uuid.uuid4()),
                timestamp=time.time(),
                metadata=instance.metadata,
            )
        )

@receiver(post_delete, sender=EmbedObject)
async def embed_object_deleted(sender, instance, **kwargs):
    """delete the embed from vector db"""
    logger.info(f"<kitchenai_core>: EmbedObject deleted: {instance.pk}")
    await whisk.embed_delete(
        EmbedRequestMessage(
            id=instance.id,
            label=instance.ingest_label,
            client_id=instance.bento_box.client_id,
            request_id=str(uuid.uuid4()),
            timestamp=time.time(),
            metadata=instance.metadata,
        )
    )
