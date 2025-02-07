import logging
import os
import sys
from importlib import import_module
from typing import TYPE_CHECKING

from django.apps import apps
from django.conf import settings
from kitchenai.contrib.kitchenai_sdk.kitchenai import KitchenAIApp
from kitchenai.core.models import KitchenAIManagement
from django.conf import settings
from django.utils import timezone
from datetime import datetime

if TYPE_CHECKING:
    from ninja import NinjaAPI
from django_q.tasks import async_task

logger = logging.getLogger("kitchenai.core.utils")


def run_django_q_task(task_name: str, *args, **kwargs):
    if settings.KITCHENAI_LOCAL:
        # Split task name into module path and function name
        # e.g. 'deepeval_plugin.tasks.run_contextual_relevancy' ->
        # module_path='deepeval_plugin.tasks', function_name='run_contextual_relevancy'
        module_path, function_name = task_name.rsplit(".", 1)

        # Import the module dynamically
        module = __import__(module_path, fromlist=[function_name])

        # Get the function from the module
        task_func = getattr(module, function_name)

        # Execute the function directly with provided args
        result = task_func(*args, **kwargs)
        return result
    async_task(task_name, *args, **kwargs)


# # Example usage
# naive_time = datetime.now()  # Your naive datetime from the database
# aware_time = make_aware(naive_time)  # Now it's timezone-aware
# Convert naive to aware
def make_aware(naive_datetime):
    return timezone.make_aware(naive_datetime, timezone=timezone.get_current_timezone())


def get_bento_clients_by_user(user):
    # TODO: return just filter functions and grab the BentoClient using the models and settings functions. to keep it entirely agnostic except for filter.
    if settings.KITCHENAI_LICENSE == "oss":
        from kitchenai.core.auth.oss.organization import OSSBentoClient

        oss_bento_clients = (
            OSSBentoClient.objects.select_related("organization")
            .filter(organization__ossorganizationmember__user=user)
            .all()
        )
        return oss_bento_clients
    else:
        # TODO: add the cloud bento section
        return OSSBentoClient.objects.filter(
            organization__ossorganizationmember__user=user
        )
