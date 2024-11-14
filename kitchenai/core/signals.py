from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.apps import apps
from kitchenai.contrib.kitchenai_sdk.tasks import process_file_task_core, delete_file_task_core
from kitchenai.contrib.kitchenai_sdk.hooks import process_file_hook_core, delete_file_hook_core
from django_q.tasks import async_task

from .models import FileObject
import logging
logger = logging.getLogger(__name__)


@receiver(post_save, sender=FileObject)
def file_object_created(sender, instance, created, **kwargs):
    """
    This signal is triggered when a new FileObject is created.
    This will trigger any listeners with matching labels and run them as async tasks
    """

    if created:
        #Ninja api should have all bolted on routes and a storage tasks
        logger.info(f"<kitchenai_core>: FileObject created: {instance.pk}")
        core_app = apps.get_app_config("core")
        if core_app.kitchenai_app:
            f = core_app.kitchenai_app.storage_tasks(instance.ingest_label)
            if f:
                async_task(process_file_task_core, instance, hook=process_file_hook_core)
            else:
                logger.warning(f"No storage task found for {instance.ingest_label}")
        else:
            logger.warning("module: no kitchenai app found")



@receiver(post_delete, sender=FileObject)
def file_object_deleted(sender, instance, **kwargs):
    """delete the file from vector db"""
    logger.info(f"<kitchenai_core>: FileObject created: {instance.pk}")
    core_app = apps.get_app_config("core")
    if core_app.kitchenai_app:
        f = core_app.kitchenai_app.storage_delete_tasks(instance.ingest_label)
        if f:
            async_task(delete_file_task_core,instance, hook=delete_file_hook_core)
        else:
            logger.warning(f"No storage task found for {instance.ingest_label}")
    else:
        logger.warning("module: no kitchenai app found")