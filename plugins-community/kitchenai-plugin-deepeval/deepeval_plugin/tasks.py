import logging
from deepeval.metrics import (
    AnswerRelevancyMetric,
    FaithfulnessMetric, 
    ContextualRelevancyMetric,
    HallucinationMetric,
    ToxicityMetric
)
from deepeval.test_case import LLMTestCase
from .models import (
    AnswerRelevance,
    Faithfulness,
    ContextualRelevancy, 
    Hallucination,
    Toxicity,
    Data
)

from .types import TestResultReason

logger = logging.getLogger(__name__)


def run_answer_relevance(data_id):
    try:
        data = Data.objects.get(id=data_id)
        if not data.retrieval_context:
            logger.warning("Skipping answer relevance check - no context available")
            AnswerRelevance.objects.create(
                data=data,
                statements=[],
                verdicts=[],
                score=0.0,
                reason=TestResultReason.NO_RETRIEVAL_CONTEXT,
                success=False,
                verbose_logs=[]
            )

            return
        context = [source["text"] for source in data.retrieval_context]

        test_case = LLMTestCase(
            input=data.input,
            actual_output=data.output,
            retrieval_context=context
        )
        metric = AnswerRelevancyMetric()
        metric.measure(test_case)

        verdicts = [verdict.model_dump() for verdict in metric.verdicts]
        AnswerRelevance.objects.create(
            data=data,
            statements=metric.statements,
            verdicts=verdicts,
            score=metric.score,
            reason=metric.reason,
            success=metric.success,
            verbose_logs=metric.verbose_logs
        )
    except Exception as e:
        logger.error(f"Error in answer relevance task: {str(e)}")
        raise

def run_faithfulness(data_id):
    try:
        data = Data.objects.get(id=data_id)
        if not data.retrieval_context:
            logger.warning("Skipping faithfulness check - no context available")
            Faithfulness.objects.create(
                data=data,
                verdicts=[],
                score=0.0,
                reason=TestResultReason.NO_RETRIEVAL_CONTEXT,
                success=False,
                verbose_logs=[]
            )
            return
        context = [source["text"] for source in data.retrieval_context]

        test_case = LLMTestCase(
            input=data.input,
            actual_output=data.output,
            retrieval_context=context
        )
        metric = FaithfulnessMetric(include_reason=True)
        metric.measure(test_case)

        verdicts = [verdict.model_dump() for verdict in metric.verdicts]
        Faithfulness.objects.create(
            data=data,
            verdicts=verdicts,
            score=metric.score,
            reason=metric.reason,
            success=metric.success,
            verbose_logs=metric.verbose_logs
        )
    except Exception as e:
        logger.error(f"Error in faithfulness task: {str(e)}")
        raise

def run_contextual_relevancy(data_id):
    try:
        data = Data.objects.get(id=data_id)
        if not data.retrieval_context:
            logger.warning("Skipping contextual relevancy check - no context available")
            ContextualRelevancy.objects.create(
                data=data,
                score=0.0,
                reason=TestResultReason.NO_RETRIEVAL_CONTEXT,
                success=False,
                verbose_logs=[]
            )
            return
        context = [source["text"] for source in data.retrieval_context]

        test_case = LLMTestCase(
            input=data.input,
            actual_output=data.output,
            retrieval_context=context
        )
        metric = ContextualRelevancyMetric(threshold=0.7, include_reason=True)
        metric.measure(test_case)

        ContextualRelevancy.objects.create(
            data=data,
            score=metric.score,
            reason=metric.reason,
            success=metric.success,
            verbose_logs=metric.verbose_logs
        )
    except Exception as e:
        logger.error(f"Error in contextual relevancy task: {str(e)}")
        raise

def run_hallucination(data_id):
    try:
        data = Data.objects.get(id=data_id)
        if not data.retrieval_context:
            logger.warning("Skipping hallucination check - no context available")
            Hallucination.objects.create(
                data=data,
                verdicts=[],
                score=0.0,
                reason=TestResultReason.NO_RETRIEVAL_CONTEXT,
                success=False,
                verbose_logs=[]
            )
            return
        context = [source["text"] for source in data.retrieval_context]

    
        test_case = LLMTestCase(
            input=data.input,
            actual_output=data.output,
            context=context
        )
        metric = HallucinationMetric(threshold=0.5, include_reason=True)
        metric.measure(test_case)

        verdicts = [verdict.model_dump() for verdict in metric.verdicts]
        Hallucination.objects.create(
            data=data,
            verdicts=verdicts,
            score=metric.score,
            reason=metric.reason,
            success=metric.success,
            verbose_logs=metric.verbose_logs
        )
    except Exception as e:
        logger.error(f"Error in hallucination task: {str(e)}")
        raise

def run_toxicity(data_id):
    try:
        data = Data.objects.get(id=data_id)
        test_case = LLMTestCase(
            input=data.input,
            actual_output=data.output
        )
        metric = ToxicityMetric(threshold=0.5, include_reason=True)
        metric.measure(test_case)

        verdicts = [verdict.model_dump() for verdict in metric.verdicts]
        Toxicity.objects.create(
            data=data,
            verdicts=verdicts,
            score=metric.score,
            reason=metric.reason,
            success=metric.success,
            verbose_logs=metric.verbose_logs
        )
    except Exception as e:
        logger.error(f"Error in toxicity task: {str(e)}")
        raise
