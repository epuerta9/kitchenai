import logging

from django.apps import apps
from django.db.models.signals import post_delete
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_q.tasks import async_task
from kitchenai.contrib.kitchenai_sdk.hooks import (
    delete_file_hook_core,
    process_file_hook_core,
)

import posthog
from ..models import FileObject

from django.dispatch import Signal
from enum import StrEnum
from django.conf import settings

logger = logging.getLogger(__name__)


class StorageSignalSender(StrEnum):
    POST_STORAGE_PROCESS = "post_storage_process"
    PRE_STORAGE_PROCESS = "pre_storage_process"
    POST_STORAGE_DELETE = "post_storage_delete"
    PRE_STORAGE_DELETE = "pre_storage_delete"


storage_signal = Signal()


@receiver(post_save, sender=FileObject)
def file_object_created(sender, instance, created, **kwargs):
    """
    This signal is triggered when a new FileObject is created.
    This will trigger any listeners with matching labels and run them as async tasks
    """

    if created:
        # Ninja api should have all bolted on routes and a storage tasks
        logger.info(f"<kitchenai_core>: FileObject created: {instance.pk}")
        posthog.capture("file_object", "kitchenai_file_object_created")

        core_app = apps.get_app_config("core")
        if core_app.kitchenai_app:
            f = core_app.kitchenai_app.storage.get_task(instance.ingest_label)
            if f:
                if settings.KITCHENAI_LOCAL:
                    from kitchenai.contrib.kitchenai_sdk.tasks import process_file_task_core
                    result = process_file_task_core(instance)
                    if result:
                        process_file_hook_core({"ingest_label": instance.ingest_label, "result": result})
                else:
                    async_task(
                        "kitchenai.contrib.kitchenai_sdk.tasks.process_file_task_core", instance, hook=process_file_hook_core
                    )
            else:
                logger.warning(
                    f"No on create handler found for {instance.ingest_label}"
                )
        else:
            logger.warning("module: no kitchenai app found")


@receiver(post_delete, sender=FileObject)
def file_object_deleted(sender, instance, **kwargs):
    """delete the file from vector db"""
    logger.info(f"<kitchenai_core>: FileObject created: {instance.pk}")
    core_app = apps.get_app_config("core")
    if core_app.kitchenai_app:
        f = core_app.kitchenai_app.storage.get_hook(instance.ingest_label, "on_delete")
        if f:
            if settings.KITCHENAI_LOCAL:
                from kitchenai.contrib.kitchenai_sdk.tasks import delete_file_task_core
                result = delete_file_task_core(instance)
                if result:
                    delete_file_hook_core({"ingest_label": instance.ingest_label, "result": result})
            else:
                async_task(
                    "kitchenai.contrib.kitchenai_sdk.tasks.delete_file_task_core",
                    instance,
                    hook=delete_file_hook_core,
                )
        else:
            logger.warning(f"No on delete task found for {instance.ingest_label}")
    else:
        logger.warning("module: no kitchenai app found")
