import json
from typing import List

from temporalio import activity

from dataclasses import dataclass
from temporalio import activity
from importlib import import_module, reload
import sys
from kitchenai.core.temporal_utils import get_agent
@dataclass
class ChatMessage:
    message: str





class CoreManagerActivities:
    def __init__(self, module: str) -> None:
        """Core manager understands the available activies based on descriptions
        and chooses to build the correct Bento Box workflow"""
        self.module = module

    @activity.defn
    async def chat(self, message: ChatMessage) -> str:
        activity.logger.info(f"Starting chat with message: {message.message}")
        
        try:

            agent = get_agent(self.module)

            response = await agent.achat(message.message)
            activity.logger.info(f"Chat response: {response}")
            return response

            
        except Exception as e:
            activity.logger.error(f"Error in chat activity: {str(e)}")
            raise

