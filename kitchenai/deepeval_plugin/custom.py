from llama_index.llms.litellm import LiteLLM
from deepeval.models import DeepEvalBaseLLM
from django.conf import settings
from pydantic import BaseModel


class CustomLiteLLM(DeepEvalBaseLLM):
    def __init__(self):
        self.model = LiteLLM(settings.LITELLM_PROVIDER)

    def load_model(self):
        return self.model

    def generate(self, prompt: str, schema: BaseModel) -> str:
        model = self.load_model()
        resp = model.complete(prompt)
        return resp.text

    async def a_generate(self, prompt: str, schema: BaseModel) -> str:
        print(prompt)
        resp = await self.model.acomplete(prompt)
        return resp.text

    def get_model_name(self):
        return settings.LITELLM_PROVIDER