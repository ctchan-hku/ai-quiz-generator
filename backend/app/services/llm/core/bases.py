"""Abstract bases that compose `complete_chat` and `parse_llm_with_retry`"""

from abc import ABC, abstractmethod
from typing import Any, ClassVar, Generic, TypeVar

from openai import AsyncOpenAI

from app.services.parser import LlmParseRetrySpec, make_llm_parse_retry_spec, parse_llm_with_retry
from app.services.llm.openai.client import CHAT_COMPLETION_KWARGS, complete_chat

T = TypeVar("T")


class BaseChatGeneration(ABC):
    """`build_messages` + one `complete_chat`. Subclasses can override `_chat_completion`."""

    _JSON_OUTPUT_INTRO = (
        "You must ALWAYS respond with valid JSON in this exact format:\n\n"
    )
    _JSON_OUTPUT_OUTRO = (
        "No ambiguity. No parsing headaches. Production‑ready.\n"
        "Do not include any text outside the JSON object. Only output the JSON."
    )

    #: Maps `_system_prompt` parameter names to markdown `#` headings. Order is preserved (Py 3.7+).
    _SYSTEM_OPTIONAL_SECTIONS: ClassVar[dict[str, str]] = {
        "context": "Context",
        "constraints": "Constraints",
        "examples": "Examples",
        "chain_of_thought": "Chain of Thought",
    }

    @property
    def class_name(self) -> str:
        return type(self).__name__

    @property
    @abstractmethod
    def role_definition(self) -> str:
        """Defines the assistant’s first-person role to guide behavior, tone, and domain scope."""

    @abstractmethod
    def structured_json_format(self) -> str:
        """Concrete JSON shape (middle section only). Wrapped by output_format."""

    def output_format(self) -> str:
        middle = self.structured_json_format().strip()
        return f"{self._JSON_OUTPUT_INTRO}{middle}\n\n{self._JSON_OUTPUT_OUTRO}"

    def _system_prompt(
        self,
        context: str,
        constraints: str,
        examples: str = "",
        chain_of_thought: str = "",
    ) -> str:
        """Role, then any non-empty optional sections, then output format."""
        sections: list[str] = [f"# Role\n{self.role_definition.strip()}"]

        stripped: dict[str, str] = {
            "context": context.strip(),
            "constraints": constraints.strip(),
            "examples": examples.strip(),
            "chain_of_thought": chain_of_thought.strip(),
        }
        for field, heading in self._SYSTEM_OPTIONAL_SECTIONS.items():
            body = stripped[field]
            if body:
                sections.append(f"# {heading}\n{body}")

        out_fmt = self.output_format().strip()
        sections.append(f"# Output Format\n{out_fmt}")

        return "\n\n".join(sections)

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
