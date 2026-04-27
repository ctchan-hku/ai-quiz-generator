"""Abstract bases that compose `complete_chat` and `parse_llm_with_retry` (shared by quiz and single-MCQ)."""

from abc import ABC, abstractmethod
from typing import Any, ClassVar, Generic, TypeVar

from openai import AsyncOpenAI

from app.services.parser import LlmParseRetrySpec, parse_llm_with_retry
from app.services.llm.common import complete_chat

T = TypeVar("T")


class BaseChatGeneration(ABC):
    """`build_messages` + one `complete_chat`. Subclasses set `WORKFLOW_ID` and `_chat_completion`."""

    WORKFLOW_ID: ClassVar[str]

    @abstractmethod
    def build_messages(self) -> list[dict[str, Any]]: ...

    @property
    def _chat_log_label(self) -> str:
        return f"generate_{self.WORKFLOW_ID.replace('-', '_')}"

    @property
    @abstractmethod
    def _chat_completion(self) -> dict[str, Any]: ...

    async def generate(self, model: str, client: AsyncOpenAI) -> tuple[str, list]:
        messages = self.build_messages()
        return await complete_chat(
            client,
            model,
            messages,
            log_label=self._chat_log_label,
            completion=self._chat_completion,
        )


class BaseLlmJsonParse(ABC, Generic[T]):
    """`parse` + `retry_spec`; `parse_with_retry` passes `self.parse` into `parse_llm_with_retry`."""

    @abstractmethod
    def parse(self, raw: str) -> T: ...

    @property
    @abstractmethod
    def retry_spec(self) -> LlmParseRetrySpec: ...

    async def parse_with_retry(
        self,
        raw: str,
        client: AsyncOpenAI,
        messages: list,
        *,
        chat_completion_kwargs: dict[str, Any],
    ) -> T:
        return await parse_llm_with_retry(
            raw,
            client,
            messages,
            parse=self.parse,
            spec=self.retry_spec,
            chat_completion_kwargs=chat_completion_kwargs,
        )
