
from abc import ABC, abstractmethod
from llama_index.core.agent import ReActAgent
from llama_index.llms.openai import OpenAI
from llama_index.core.tools import FunctionTool
from kitchenai.core.tools import multiply
from llama_index.core.llms import ChatMessage

class BaseAgent(ABC):
    @abstractmethod
    async def achat(self, message: str) -> str:
        pass

class CoreAgent(BaseAgent):
    def __init__(self) -> None:
        self.llm = OpenAI(model="gpt-3.5-turbo", temperature=1)
        multiply_tool = FunctionTool.from_defaults(fn=multiply)
        self.agent = ReActAgent.from_tools([], llm=self.llm, verbose=True)

    async def achat(self, message: str) -> str:
        #response = await self.agent.achat(message)
        messages = [
            ChatMessage(
                role="system", content="You are a pirate with a colorful personality"
            ),
            ChatMessage(role="user", content=message),
        ]

        response = await self.llm.achat(messages)
        message_blocks = []
        for r in response.message.blocks:
            message_blocks.append(r.text)
        return " ".join(message_blocks)



class LLMAgent(BaseAgent):
    def __init__(self) -> None:
        self.llm = OpenAI(model="gpt-3.5-turbo", temperature=1)

    async def achat(self, message: str) -> str:
        return await self.llm.achat(message)