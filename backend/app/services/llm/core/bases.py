"""Abstract bases that compose `complete_chat` and `parse_llm_with_retry`"""

from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from openai import AsyncOpenAI

from app.services.parser import LlmParseRetrySpec, make_llm_parse_retry_spec, parse_llm_with_retry
from app.services.llm.openai.client import CHAT_COMPLETION_KWARGS, complete_chat

T = TypeVar("T")


class BaseChatGeneration(ABC):
    """`build_messages` + one `complete_chat`. Subclasses can override `_chat_completion`."""

    @property
    def class_name(self) -> str:
        return type(self).__name__

    @property
    @abstractmethod
    def role_definition(self) -> str:
        """First-person role line for the system prompt Role section."""

    @abstractmethod
    def output_format(self) -> str:
        """Output-shape snippet between role and field rules (include the word ``json`` for JSON mode APIs)."""

    def _system_prompt(
        self,
        task: str,
        constraints: str,
        examples: str = "",
        chain_of_thought: str = "",
    ) -> str:
        """Role + Task + Constraints + Examples + Chain of Thought + Output Format."""
        blocks = [
            f"# Role\n{self.role_definition}",
            f"# Task\n{task}",
            f"# Constraints\n{constraints.strip()}",
        ]
        if examples:
            blocks.append(f"# Examples\n{examples.strip()}")
        if chain_of_thought:
            blocks.append(f"# Chain of Thought\n{chain_of_thought.strip()}")

        blocks.append(f"# Output Format\n{self.output_format().strip()}")
        return "\n\n".join(blocks)

    @abstractmethod
    def build_messages(self) -> list[dict[str, Any]]: ...

    @property
    def _chat_log_label(self) -> str:
        return f"generate_{self.class_name}"

    @property
    def _chat_completion(self) -> dict[str, Any]:
        return CHAT_COMPLETION_KWARGS

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
    """Read what the model returned and build a typed, validated result.

    Subclasses implement parse to unpack the reply and check it fits the schema.
    If that fails, parse_with_retry asks the model for a corrected reply and tries again.
    """

    @abstractmethod
    def parse(self, raw: str) -> T:
        """Turn one assistant message string into the validated result object."""

    @property
    def retry_spec(self) -> LlmParseRetrySpec:
        return make_llm_parse_retry_spec(class_name=type(self).__name__)

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
