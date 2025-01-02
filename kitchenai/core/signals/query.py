import logging

from django.apps import apps
from django.db.models.signals import post_delete
from django.db.models.signals import post_save
from django.dispatch import receiver, Signal
from django_q.tasks import async_task

import posthog
logger = logging.getLogger(__name__)

from enum import StrEnum

class QuerySignalSender(StrEnum):
    POST_API_QUERY = "post_api_query"
    PRE_API_QUERY = "pre_api_query"
    POST_DASHBOARD_QUERY = "post_dashboard_query"
    PRE_DASHBOARD_QUERY = "pre_dashboard_query"


query_signal = Signal()

# @receiver(query_input_signal)
# def my_signal_handler(sender, **kwargs):
#     print(f"Signal received from {sender}. Additional data: {kwargs}")

@receiver(query_signal, sender=QuerySignalSender.POST_API_QUERY)
async def query_output_handler(sender, **kwargs):
    pass

@receiver(query_signal, sender=QuerySignalSender.POST_DASHBOARD_QUERY)
async def query_output_handler(sender, **kwargs):
    pass