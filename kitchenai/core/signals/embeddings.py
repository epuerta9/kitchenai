import logging

from django.apps import apps
from django.db.models.signals import post_delete
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_q.tasks import async_task
from kitchenai.contrib.kitchenai_sdk.tasks import embed_task_core, delete_embed_task_core
import posthog
from ..models import EmbedObject

logger = logging.getLogger(__name__)



@receiver(post_save, sender=EmbedObject)
def embed_object_created(sender, instance, created, **kwargs):
    """
    This signal is triggered when a new EmbedObject is created.
    This will trigger any listeners with matching labels and run them as async tasks
    """
    if created:
        logger.info(f"<kitchenai_core>: EmbedObject created: {instance.pk}")
        posthog.capture("embed_object", "kitchenai_embed_object_created")

        core_app = apps.get_app_config("core")
        if core_app.kitchenai_app:
            f = core_app.kitchenai_app.embeddings.get_task(instance.ingest_label)
            if f:
                #TODO: add hook
                async_task(embed_task_core, instance)
            else:
                logger.warning(f"No embed task found for {instance.ingest_label}")
        else:
            logger.warning("module: no kitchenai app found")

@receiver(post_delete, sender=EmbedObject)
def embed_object_deleted(sender, instance, **kwargs):
    """delete the embed from vector db"""
    logger.info(f"<kitchenai_core>: EmbedObject deleted: {instance.pk}")
    core_app = apps.get_app_config("core")
    if core_app.kitchenai_app:
        f = core_app.kitchenai_app.embeddings.get_hook(instance.ingest_label, "on_delete")
        if f:
            #TODO: add hook
            async_task(delete_embed_task_core, instance)
        else:
            logger.warning(f"No embed delete task found for {instance.ingest_label}")
    else:
        logger.warning("module: no kitchenai app found")
