from .models import ChatMetric, AggregatedChatMetric
import logging
from django.db import models    
logger = logging.getLogger(__name__)

#dashboard tasks

def update_aggregated_metrics(instance):
    logger.info(f"Creating aggregated metrics for chat {instance.chat}")
    metrics, _ = AggregatedChatMetric.objects.get_or_create(chat=instance.chat)

    # Get all metrics for this chat
    all_metrics = ChatMetric.objects.filter(chat=instance.chat).all()
    
    # Calculate new aggregated values
    metrics.avg_response_time = all_metrics.aggregate(avg=models.Avg('response_time'))['avg']
    metrics.total_token_usage = all_metrics.aggregate(sum=models.Sum('token_usage'))['sum']
    metrics.avg_confidence_score = all_metrics.aggregate(avg=models.Avg('confidence_score'))['avg']
    metrics.total_interactions = all_metrics.count()
    
    metrics.save()
