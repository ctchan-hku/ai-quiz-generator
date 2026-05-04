"""Structural contracts for message+completion and LLM JSON parse+retry (shared by quiz and single-MCQ)."""

from typing import Any, Generic, Protocol, TypeVar, runtime_checkable

from openai import AsyncOpenAI

from app.models.token_usage import TokenUsage
from app.services.parser import LlmParseRetrySpec

T_co = TypeVar("T_co", covariant=True)


@runtime_checkable
class LLMGeneration(Protocol):
    def build_messages(self) -> list[dict[str, Any]]: ...

    async def generate(
        self, model: str, client: AsyncOpenAI
    ) -> tuple[str, list[dict[str, Any]], TokenUsage]: ...


@runtime_checkable
class LlmJsonParse(Protocol, Generic[T_co]):
    """`parse` + `retry_spec`; `parse_with_retry` after a bad completion."""

    @property
    def retry_spec(self) -> LlmParseRetrySpec: ...

    def parse(self, raw: str) -> T_co: ...

    async def parse_with_retry(
        self,
        raw: str,
        client: AsyncOpenAI,
        messages: list,
        *,
        chat_completion_kwargs: dict[str, Any],
        initial_usage: TokenUsage | None = None,
    ) -> tuple[T_co, TokenUsage]: ...
