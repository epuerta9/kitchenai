import logging

from kitchenai.contrib.kitchenai_sdk.schema import QueryBaseResponseSchema
from django.dispatch import receiver, Signal

from enum import StrEnum

logger = logging.getLogger(__name__)

class QuerySignalSender(StrEnum):
    POST_API_QUERY = "post_api_query"
    PRE_API_QUERY = "pre_api_query"
    POST_DASHBOARD_QUERY = "post_dashboard_query"
    PRE_DASHBOARD_QUERY = "pre_dashboard_query"


query_signal = Signal()


@receiver(query_signal, sender=QuerySignalSender.POST_API_QUERY)
async def query_output_handler(sender, **kwargs):

    pass

