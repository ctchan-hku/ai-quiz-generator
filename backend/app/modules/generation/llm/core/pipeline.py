from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from langchain_core.language_models.chat_models import BaseChatModel
from pydantic import BaseModel

from app.integrations.langchain.structured_step import StructuredLlmStep
from app.integrations.openai.token_usage import TokenUsage
from app.modules.generation.helpers.cost import calculate_cost

TStep = TypeVar("TStep", bound=BaseModel)
TResult = TypeVar("TResult")


class BasePipeline(ABC, Generic[TResult]):
    def __init__(self) -> None:
        self.token_usage = TokenUsage()

    @abstractmethod
    async def _run(self, model: str, llm: BaseChatModel) -> TResult: ...

    async def run(self, model: str, llm: BaseChatModel) -> tuple[TResult, float]:
        result = await self._run(model, llm)
        return result, calculate_cost(model, self.token_usage)

    async def _run_generator_step(
        self,
        step: StructuredLlmStep[TStep],
        model: str,
        llm: BaseChatModel,
    ) -> TStep:
        parsed, step_usage = await step.run(model, llm)
        self.token_usage += step_usage
        return parsed


__all__ = ["BasePipeline", "StructuredLlmStep"]
