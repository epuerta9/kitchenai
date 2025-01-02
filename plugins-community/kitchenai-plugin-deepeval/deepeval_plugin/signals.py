from django.dispatch import receiver
from django.db.models.signals import post_save
import logging
from deepeval.metrics import AnswerRelevancyMetric
from deepeval.test_case import LLMTestCase
from .models import Data
from .utils import is_enabled
from .models import AnswerRelevance

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Data)
async def answer_relevance_post_save(sender, instance, **kwargs):
    if is_enabled():
        context = [source["text"] for source in instance.retrieval_context]

        test_case = LLMTestCase(
            input=instance.input,
            actual_output=instance.output,
            retrieval_context=context
        )
        answer_relevancy_metric = AnswerRelevancyMetric()

        answer_relevancy_metric.measure(test_case)

        verdicts = [verdict.model_dump() for verdict in answer_relevancy_metric.verdicts]
        await AnswerRelevance.objects.acreate(
            data=instance,
            statements=answer_relevancy_metric.statements,
            verdicts=verdicts, 
            score=answer_relevancy_metric.score,
            reason=answer_relevancy_metric.reason,
            success=answer_relevancy_metric.success,
            verbose_logs=answer_relevancy_metric.verbose_logs
        )
