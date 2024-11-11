import logging  
logger = logging.getLogger(__name__)    

def process_data_hook(task):
    logger.info(f"process_data_hook: {task.result}")