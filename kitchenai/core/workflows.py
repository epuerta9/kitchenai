import asyncio
from collections import deque
from dataclasses import dataclass
from datetime import timedelta
from typing import Deque, List, Optional, Tuple

from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    pass

@dataclass
class CoreParams:
    message: str = None

@dataclass
class ChatSignal:
    message: str = None
    user_id: str = None
    metadata: dict = {}

@dataclass
class ChatEndSignal:
    user_id: str = None
    metadata: dict = {}

@workflow.defn
class KitchenAICoreWorkflow:
    def __init__(self) -> None:
        # List to store prompt history
        self.messages: List[ChatSignal] = []
        self.is_chat_ended: bool = False

    @workflow.run
    async def run(
        self,
        params: CoreParams,
    ) -> str:
        while True:
            await workflow.wait_condition(
                lambda: self.is_chat_ended
            )
            print(f"Messages queue: {self.messages}")

    @workflow.signal
    async def chat(self, chat_signal: ChatSignal) -> None:
        # Chat ended but the workflow is waiting for a chat summary to be generated
        if self.is_chat_ended:
            workflow.logger.warn(f"Message dropped due to chat closed: {chat_signal.message}")
            return
        else:
            return "Hello-chat"


    @workflow.signal
    async def end_chat(self) -> None:
        self.is_chat_ended = True

    @workflow.query
    def get_conversation_history(self) -> List[Tuple[str, str]]:
        return self.messages

    @workflow.query
    def get_summary_from_history(self) -> Optional[str]:
        return "Summary"

