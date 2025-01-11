import json
from typing import List

from temporalio import activity
import asyncio


class CoreManagerActivities:
    def __init__(self) -> None:
        """Core manager understands the available activies based on descriptions
        and chooses to build the correct Bento Box workflow"""
        self.role: str = None
        self.capabilities: List[str] = []

    @activity.defn
    async def chat(self, message: str) -> str:
        # Model params
        modelId = "meta.llama2-70b-chat-v1"
        accept = "application/json"
        contentType = "application/json"
        max_gen_len = 512
        temperature = 0.1
        top_p = 0.2

        body = json.dumps(
            {
                "prompt": " message",
                "max_gen_len": max_gen_len,
                "temperature": temperature,
                "top_p": top_p,
            }
        )

        response = await asyncio.sleep(1)

        return body