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
    metrics.embedding_tokens = all_metrics.aggregate(sum=models.Sum('embedding_tokens'))['sum'] or 0
    metrics.llm_prompt_tokens = all_metrics.aggregate(sum=models.Sum('llm_prompt_tokens'))['sum'] or 0
    metrics.llm_completion_tokens = all_metrics.aggregate(sum=models.Sum('llm_completion_tokens'))['sum'] or 0
    metrics.total_llm_tokens = all_metrics.aggregate(sum=models.Sum('total_llm_tokens'))['sum'] or 0
    metrics.total_interactions = all_metrics.count()
    
    metrics.save()
