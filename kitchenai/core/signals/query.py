import logging

from django.apps import apps
from django.db.models.signals import post_delete
from django.db.models.signals import post_save
from django.dispatch import receiver, Signal
from django_q.tasks import async_task
from kitchenai.contrib.kitchenai_sdk.hooks import delete_file_hook_core, process_file_hook_core
from kitchenai.contrib.kitchenai_sdk.tasks import delete_file_task_core, process_file_task_core, embed_task_core, delete_embed_task_core
import posthog
logger = logging.getLogger(__name__)


query_input_signal = Signal()
query_output_signal = Signal()

@receiver(query_input_signal)
def my_signal_handler(sender, **kwargs):
    print(f"Signal received from {sender}. Additional data: {kwargs}")

@receiver(query_output_signal)
def query_output_handler(sender, **kwargs):
    print(f"Signal received from {sender}. Additional data: {kwargs}")