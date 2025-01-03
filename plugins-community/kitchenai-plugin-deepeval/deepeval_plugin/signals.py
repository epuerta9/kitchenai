from django.dispatch import receiver
from django.db.models.signals import post_save
import logging
from .models import Data, Settings

from kitchenai.core.utils import run_django_q_task
logger = logging.getLogger(__name__)

@receiver(post_save, sender=Data)
def answer_relevance_post_save(sender, instance, **kwargs):
    setting = Settings.get_settings()
    if setting.is_answer_relevance_enabled:
        if kwargs.get("error"):
            return
        run_django_q_task('deepeval_plugin.tasks.run_answer_relevance', instance.id)

@receiver(post_save, sender=Data)
def faithfulness_post_save(sender, instance, **kwargs):
    setting = Settings.get_settings()
    if setting.is_faithfulness_enabled:
        if kwargs.get("error"):
            return
        run_django_q_task('deepeval_plugin.tasks.run_faithfulness', instance.id)

@receiver(post_save, sender=Data)
def contextual_relevancy_post_save(sender, instance, **kwargs):
    setting = Settings.get_settings()
    if setting.is_contextual_relevancy_enabled:
        if kwargs.get("error"):
            return
        run_django_q_task('deepeval_plugin.tasks.run_contextual_relevancy', instance.id)

@receiver(post_save, sender=Data)
def hallucination_post_save(sender, instance, **kwargs):
    setting = Settings.get_settings()
    if setting.is_hallucination_enabled:
        if kwargs.get("error"):
            return
        run_django_q_task('deepeval_plugin.tasks.run_hallucination', instance.id)

@receiver(post_save, sender=Data)
def toxicity_post_save(sender, instance, **kwargs):
    setting = Settings.get_settings()
    if setting.is_toxicity_enabled:
        if kwargs.get("error"):
            return
        run_django_q_task('deepeval_plugin.tasks.run_toxicity', instance.id)

