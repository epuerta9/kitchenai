# from kitchenai.contrib.kitchenai_sdk.schema import QuerySchema
# import logging
# from django.apps import apps
# from kitchenai.core.utils import get_core_kitchenai_app, add_bento_box_to_core
# import asyncio
# logger = logging.getLogger(__name__)

# def agent_task(data: QuerySchema, stream_id: str, label: str):

#     loop = asyncio.new_event_loop()
#     asyncio.set_event_loop(loop)
#     try:
#         kitchenai_app = apps.get_app_config("core").kitchenai_app
#         if not kitchenai_app:
#             logger.error("No kitchenai app in core app config")
#             raise Exception("No kitchenai app in core app config")
#         query_func = kitchenai_app.query.get_task(label)
#         if not query_func:
#             logger.error(f"Query function not found for {label}")
#             raise Exception(f"Query function not found for {label}")
        
#         result = query_func(data)

#         print(result)
#         return result
#     finally:
#         loop.close()
#     add_bento_box_to_core()
#     try:

#     except Exception as e:
#         logger.error(f"Error in query_stream_task: {e}")
#         raise e

