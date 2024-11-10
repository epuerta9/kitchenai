from django.db.models.signals import post_save
from django.dispatch import receiver
from django.apps import apps
from kitchenai.contrib.kitchenai_sdk.tasks import process_file_task
from django_q.tasks import async_task, result

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
        logger.debug(f"FileObject created: {instance.pk}")
        core_app = apps.get_app_config("core")
        if core_app.kitchenai_app:
            f = core_app.kitchenai_app.storage_tasks(instance.ingest_label)
            hook = core_app.kitchenai_app.success_hooks(instance.ingest_label)
            if f:
                async_task(process_file_task,f, instance, hook=hook)
            else:
                logger.warning(f"No storage task found for {instance.ingest_label}")
        else:
            logger.warning("module: no kitchenai app found")
