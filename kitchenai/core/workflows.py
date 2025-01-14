import asyncio
from collections import deque
from dataclasses import dataclass, field
from datetime import timedelta
from typing import Deque, List, Optional, Tuple, Dict, Any
from temporalio.common import RetryPolicy

from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from kitchenai.core.activities import CoreManagerActivities, ChatMessage


@dataclass
class CoreParams:
    message: Optional[str] = field(default=None)


@dataclass
class ChatSignal:
    message: Optional[str] = field(default=None)
    user_id: Optional[str] = field(default=None)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ChatEndSignal:
    user_id: Optional[str] = field(default=None)
    metadata: Dict[str, Any] = field(default_factory=dict)


@workflow.defn
class KitchenAICoreWorkflow:
    def __init__(self) -> None:
        self.messages: List[ChatSignal] = []
        self.is_chat_ended: bool = False
        self.is_cancel_requested: bool = False
        self._continue_as_new_threshold = 250

    async def _continue_as_new_if_needed(self, params: CoreParams) -> None:
        """Handle workflow continuation if history limit is reached."""
        if len(self.messages) >= self._continue_as_new_threshold:
            workflow.logger.info(
                f"Message length {len(self.messages)} exceeded threshold "
                f"{self._continue_as_new_threshold}, continuing as new"
            )
            
            # Get conversation summary before continuing
            summary = await workflow.execute_activity(
                CoreManagerActivities.summarize_chat,
                args=[self.messages],
                schedule_to_close_timeout=timedelta(seconds=30),
                retry_policy=RetryPolicy(
                    maximum_attempts=3,
                    initial_interval=timedelta(seconds=5)
                )
            )
            
            # Continue as new with current state
            workflow.continue_as_new(
                params,
                messages=self.messages,
                is_chat_ended=self.is_chat_ended,
                is_cancel_requested=self.is_cancel_requested,
                conversation_summary=summary
            )

    @workflow.run
    async def run(
        self,
        params: CoreParams,
        messages: Optional[List[ChatSignal]] = None,
        is_chat_ended: bool = False,
        is_cancel_requested: bool = False,
        conversation_summary: Optional[str] = None
    ) -> str:
        # Restore state if continuing
        if messages is not None:
            self.messages = messages
            self.is_chat_ended = is_chat_ended
            self.is_cancel_requested = is_cancel_requested
            
        # Add summary to messages if continuing
        if conversation_summary:
            self.messages.append(ChatSignal(
                message=f"Previous conversation summary: {conversation_summary}",
                metadata={"type": "summary"}
            ))

        try:
            while not self.is_chat_ended and not self.is_cancel_requested:
                # Check if we need to continue as new
                await self._continue_as_new_if_needed(params)
                
                # Wait indefinitely for signals
                await workflow.wait_condition(
                    lambda: self.is_chat_ended or self.is_cancel_requested
                )

            if self.is_cancel_requested:
                workflow.logger.info("Workflow cancellation requested.")
                return "Workflow cancelled."
                
            return "Chat ended normally."
            
        except asyncio.CancelledError:
            workflow.logger.info("Workflow cancelled via CancelledError")
            return "Workflow cancelled."

    @workflow.signal
    async def chat(self, chat_signal: ChatSignal) -> None:
        if self.is_chat_ended:
            workflow.logger.warn(f"Message dropped due to chat closed: {chat_signal.message}")
            return
        
        response = await workflow.execute_activity(
            CoreManagerActivities.chat,
            args=[chat_signal],
            schedule_to_close_timeout=timedelta(seconds=30),
            retry_policy=RetryPolicy(
                maximum_attempts=3,
                initial_interval=timedelta(seconds=5)
            )
        )
        workflow.logger.info(f"Response: {response}")
        self.messages.append(response)

    @workflow.signal
    async def end_chat(self) -> None:
        self.is_chat_ended = True

    @workflow.signal
    async def cancel(self) -> None:
        self.is_cancel_requested = True
        workflow.logger.info("Cancel signal received. Cancelling workflow.")

    @workflow.query
    def get_conversation_history(self) -> List[str]:
        return [msg.message for msg in self.messages]

    @workflow.query
    def get_summary_from_history(self) -> Optional[str]:
        for msg in reversed(self.messages):
            if msg.metadata.get("type") == "summary":
                return msg.message
        return None

