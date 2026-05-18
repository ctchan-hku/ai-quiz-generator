from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from pydantic import BaseModel

from app.integrations.openai.client import OpenAiChat
from app.integrations.openai.token_usage import TokenUsage
from app.modules.generation.helpers.cost import calculate_cost
from app.modules.generation.llm.core.llm_json_generator import LlmJsonGenerator

TStep = TypeVar("TStep", bound=BaseModel)
TResult = TypeVar("TResult")


class BasePipeline(ABC, Generic[TResult]):
    def __init__(self) -> None:
        self.token_usage = TokenUsage()

    @abstractmethod
    async def _run(self, model: str, llm: OpenAiChat) -> TResult: ...

    async def run(self, model: str, llm: OpenAiChat) -> tuple[TResult, float]:
        result = await self._run(model, llm)
        return result, calculate_cost(model, self.token_usage)

    async def _run_generator_step(
        self,
        generator: LlmJsonGenerator[TStep],
        model: str,
        llm: OpenAiChat,
    ) -> TStep:
        raw, messages, gen_usage = await generator.generate(model, llm)
        self.token_usage += gen_usage

        parsed, retry_usage = await generator.parse_with_retry(
            raw,
            llm,
            messages,
            model=model,
        )
        self.token_usage += retry_usage

        return parsed
