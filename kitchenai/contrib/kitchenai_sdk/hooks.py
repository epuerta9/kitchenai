import logging

from kitchenai.core.utils import get_core_kitchenai_app
logger = logging.getLogger(__name__)

def default_hook(task):
    logger.info(f"default_hook: {task.result}")



def process_file_hook_core(task):
    """process file hook for core app. We have to mock the hook function
    because it's not callable from django q."""
    try:
        kitchenai_app = get_core_kitchenai_app()
        hook = kitchenai_app.storage_create_hooks(task.result.get('ingest_label'))
        if hook:
            hook(task)
        else:
            logger.warning(f"No hook found for {task.result.get('ingest_label')}")
    except Exception as e:
        logger.error(f"Error in run_task: {e}")


def delete_file_hook_core(task):
    logger.info(f"delete_file_hook_core: {task.result}")
    try:
        kitchenai_app = get_core_kitchenai_app()
        hook = kitchenai_app.storage_delete_hooks(task.result.get('ingest_label'))
        if hook:
            hook(task)
    except Exception as e:
        logger.error(f"Error in run_task: {e}")
