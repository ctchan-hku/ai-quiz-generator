"""Abstract bases for chat completion (`build_messages` + `complete_chat`)."""

from abc import ABC, abstractmethod
from typing import Any, ClassVar

from openai import AsyncOpenAI

from app.models.token_usage import TokenUsage
from backend.app.modules.generation.openai.client import CHAT_COMPLETION_KWARGS, complete_chat


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
