from django.dispatch import receiver
from django.db.models.signals import post_save
import logging
from deepeval.metrics import AnswerRelevancyMetric
from deepeval.test_case import LLMTestCase
from .models import Data, AnswerRelevance, Faithfulness, ContextualRelevancy, Hallucination, Toxicity, Settings
from .utils import is_enabled
from deepeval.metrics import FaithfulnessMetric
from deepeval.metrics import ContextualRelevancyMetric
from deepeval.metrics import HallucinationMetric
from deepeval.metrics import ToxicityMetric

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Data)
async def answer_relevance_post_save(sender, instance, **kwargs):
    setting = await Settings.aget_settings()
    if setting.is_answer_relevance_enabled:
        if kwargs.get("error"):
            return  
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


@receiver(post_save, sender=Data)
async def faithfulness_post_save(sender, instance, **kwargs):
    setting = await Settings.aget_settings()
    if setting.is_faithfulness_enabled:
        if kwargs.get("error"):
            return  
        context = [source["text"] for source in instance.retrieval_context]

        test_case = LLMTestCase(
            input=instance.input,
            actual_output=instance.output,
            retrieval_context=context
        )
        metric = FaithfulnessMetric(
            include_reason=True
        )
        metric.measure(test_case)

        verdicts = [verdict.model_dump() for verdict in metric.verdicts]
        await Faithfulness.objects.acreate(
            data=instance,
            verdicts=verdicts, 
            score=metric.score,
            reason=metric.reason,
            success=metric.success,
            verbose_logs=metric.verbose_logs
        )


@receiver(post_save, sender=Data)
async def contextual_relevancy_post_save(sender, instance, **kwargs):
    setting = await Settings.aget_settings()
    if setting.is_contextual_relevancy_enabled:
        if kwargs.get("error"):
            return  
        context = [source["text"] for source in instance.retrieval_context]

        test_case = LLMTestCase(
            input=instance.input,
            actual_output=instance.output,
            retrieval_context=context
        )
        metric = ContextualRelevancyMetric(
            threshold=0.7,
            include_reason=True
        )
        metric.measure(test_case)

        await ContextualRelevancy.objects.acreate(
            data=instance,
            score=metric.score,
            reason=metric.reason,
            success=metric.success,
            verbose_logs=metric.verbose_logs
        )


@receiver(post_save, sender=Data)
async def hallucination_post_save(sender, instance, **kwargs):
    setting = await Settings.aget_settings()
    if setting.is_hallucination_enabled:
        if kwargs.get("error"):
            return
        context = [source["text"] for source in instance.retrieval_context]
        
        # Skip if no context is available
        if not context:
            logger.warning("Skipping hallucination check - no context available")
            return

        test_case = LLMTestCase(
            input=instance.input,
            actual_output=instance.output,
            context=context  # Changed from retrieval_context to context
        )
        metric = HallucinationMetric(
            threshold=0.5,
            include_reason=True
        )
        
        try:
            metric.measure(test_case)
            verdicts = [verdict.model_dump() for verdict in metric.verdicts]
            await Hallucination.objects.acreate(
                data=instance,
                verdicts=verdicts, 
                score=metric.score,
                reason=metric.reason,
                success=metric.success,
                verbose_logs=metric.verbose_logs
            )
        except Exception as e:
            logger.error(f"Error in hallucination metric: {str(e)}")
            raise


@receiver(post_save, sender=Data)
async def toxicity_post_save(sender, instance, **kwargs):
    setting = await Settings.aget_settings()
    if setting.is_toxicity_enabled:
        if kwargs.get("error"):
            return  
        test_case = LLMTestCase(
            input=instance.input,
            actual_output=instance.output
        )
        metric = ToxicityMetric(
            threshold=0.5,
            include_reason=True
        )
        metric.measure(test_case)

        verdicts = [verdict.model_dump() for verdict in metric.verdicts]
        await Toxicity.objects.acreate(
            data=instance,
            verdicts=verdicts, 
            score=metric.score,
            reason=metric.reason,
            success=metric.success,
            verbose_logs=metric.verbose_logs
        )

