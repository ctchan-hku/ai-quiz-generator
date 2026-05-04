"""Abstract bases that compose `complete_chat` and `parse_llm_with_retry`"""

from abc import ABC, abstractmethod
from typing import Any, ClassVar, Generic, TypeVar

from openai import AsyncOpenAI

from app.models.token_usage import TokenUsage
from app.services.parser import LlmParseRetrySpec, make_llm_parse_retry_spec, parse_llm_with_retry
from app.services.llm.openai.client import CHAT_COMPLETION_KWARGS, complete_chat

T = TypeVar("T")


class BaseChatGeneration(ABC):
    """`build_messages` + one `complete_chat`. Subclasses can override `_chat_completion`."""

    _JSON_OUTPUT_INTRO = (
        "You must ALWAYS respond with valid JSON in this exact format:"
    )
    _JSON_OUTPUT_OUTRO = (
        "No ambiguity. No parsing headaches. Production‑ready.\n"
        "Do not include any text outside the JSON object. Only output the JSON."
    )

    #: (raw body key, heading, always_emit). If always_emit is False, section is omitted when strip is empty.
    _SYSTEM_SECTIONS: ClassVar[tuple[tuple[str, str, bool], ...]] = (
        ("role", "Role", True),
        ("guidelines", "Guidelines", False),
        ("context", "Context", False),
        ("constraints", "User Instructions and Constraints", False),
        ("examples", "Examples", False),
        ("chain_of_thought", "Chain of Thought", False),
        ("output_format", "Output Format", True),
    )

    @staticmethod
    def _strip_prompt_text(text: str) -> str:
        return text.strip()

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
        return f"{self._JSON_OUTPUT_INTRO}\n\n{self.structured_json_format()}\n\n{self._JSON_OUTPUT_OUTRO}"

    def _system_prompt(
        self,
        context: str,
        constraints: str,
        guidelines: str = "",
        examples: str = "",
        chain_of_thought: str = "",
    ) -> str:
        """Build the system message from ordered sections; optional blocks skip empty bodies after strip."""
        raw_bodies: dict[str, str] = {
            "role": self.role_definition,
            "guidelines": guidelines,
            "context": context,
            "constraints": constraints,
            "examples": examples,
            "chain_of_thought": chain_of_thought,
            "output_format": self.output_format(),
        }
        sections: list[str] = []
        for field, heading, always_emit in self._SYSTEM_SECTIONS:
            body = self._strip_prompt_text(raw_bodies[field])
            if not always_emit and not body:
                continue
            sections.append(f"# {heading}\n{body}")
        return "\n\n".join(sections)

    @abstractmethod
    def build_messages(self) -> list[dict[str, Any]]: ...

    @property
    def _chat_log_label(self) -> str:
        return f"generate_{self.class_name}"

    @property
    def _chat_completion(self) -> dict[str, Any]:
        return CHAT_COMPLETION_KWARGS

    async def generate(
        self, model: str, client: AsyncOpenAI
    ) -> tuple[str, list[dict[str, Any]], TokenUsage]:
        """Return assistant text, chat messages, and usage for this completion.

        - **str** — raw assistant message content (expected JSON from the model).
        - **list** — same chat ``messages`` list sent to the API (for ``parse_with_retry`` / corrective turns).
        - **TokenUsage** — ``prompt_tokens`` / ``completion_tokens`` from this response.
        """
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
        initial_usage: TokenUsage | None = None,
    ) -> tuple[T, TokenUsage]:
        return await parse_llm_with_retry(
            raw,
            client,
            messages,
            parse=self.parse,
            spec=self.retry_spec,
            chat_completion_kwargs=chat_completion_kwargs,
            initial_usage=initial_usage,
        )
