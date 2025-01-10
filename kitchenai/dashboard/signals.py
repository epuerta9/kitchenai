#signals.py



from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ChatMetric
import logging
from django_q.tasks import async_task
logger = logging.getLogger(__name__)
from django.conf import settings

@receiver(post_save, sender=ChatMetric)
def chat_metric_created(sender, instance, created, **kwargs):
    """
    Signal handler that triggers when a new ChatMetric is created.
    Updates the aggregated metrics asynchronously.
    """
    if created:
        logger.info(f"ChatMetric created: {instance.pk}")
        if settings.KITCHENAI_LOCAL:
            from kitchenai.dashboard.tasks import update_aggregated_metrics
            update_aggregated_metrics(instance)
        else:
            async_task("kitchenai.dashboard.tasks.update_aggregated_metrics", instance)

