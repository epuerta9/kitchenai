import logging

from kitchenai.core.utils import get_core_kitchenai_app
from django.conf import settings
logger = logging.getLogger(__name__)

def default_hook(task):
    logger.info(f"default_hook: {task.result}")



def process_file_hook_core(task):
    """process file hook for core app. We have to mock the hook function
    because it's not callable from django q."""
    if settings.KITCHENAI_LOCAL:
        if task["result"]:
            try:
                kitchenai_app = get_core_kitchenai_app()
                hook = kitchenai_app.storage.get_hook(task["result"].get('ingest_label'), "on_create")
                if hook:
                    hook(task)
                else:
                    logger.warning(f"No hook found for {task['result'].get('ingest_label')}")
            except Exception as e:
                logger.error(f"Error in run_task: {e}")
            return
    if task.result:
        try:
            kitchenai_app = get_core_kitchenai_app()
            hook = kitchenai_app.storage.get_hook(task.result.get('ingest_label'), "on_create")
            if hook:
                hook(task)
            else:
                logger.warning(f"No hook found for {task.result.get('ingest_label')}")
        except Exception as e:
            logger.error(f"Error in run_task: {e}")


def delete_file_hook_core(task):
    if settings.KITCHENAI_LOCAL:
        if task["result"]:
            try:
                kitchenai_app = get_core_kitchenai_app()
                hook = kitchenai_app.storage.get_hook(task["result"].get('ingest_label'), "on_delete")
                if hook:
                    hook(task)
                else:
                    logger.warning(f"No hook found for {task['result'].get('ingest_label')}")
            except Exception as e:
                logger.error(f"Error in run_task: {e}")
            return
    if task.result:
        try:
            kitchenai_app = get_core_kitchenai_app()
            hook = kitchenai_app.storage.get_hook(task.result.get('ingest_label'), "on_delete")
            if hook:
                hook(task)
            else:
                logger.warning(f"No hook found for {task.result.get('ingest_label')}")
        except Exception as e:
            logger.error(f"Error in run_task: {e}")