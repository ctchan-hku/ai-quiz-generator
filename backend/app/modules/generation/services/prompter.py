"""Structured prompts and JSON-mode chat completion for LLM JSON responses."""

from abc import ABC, abstractmethod
from typing import Any, ClassVar

from app.integrations.openai.client import (
    MAX_COMPLETION_TOKENS,
    CompletionParams,
    OpenAiChat,
)
from app.integrations.openai.token_usage import TokenUsage
from app.modules.generation.config.prompts import JSON_OUTPUT_RULES


class LlmJsonPrompter(ABC):
    """Compose system/user prompts that steer the model toward one JSON object, then call chat completion."""

    #: (raw body key, heading, always_emit). If always_emit is False, section is omitted when strip is empty.
    _SYSTEM_SECTIONS: ClassVar[tuple[tuple[str, str, bool], ...]] = (
        ("role", "Role", True),
        ("guidelines", "Guidelines", False),
        ("context", "Context", False),
        ("requirements", "Requirements", False),
        ("examples", "Examples", False),
        ("chain_of_thought", "Chain of Thought", False),
        ("output_format", "Output Format", True),
    )

    def completion_max_tokens(self) -> int:
        """Override when a step needs a different budget; JSON mode is always applied."""
        return MAX_COMPLETION_TOKENS

    @property
    def _chat_completion(self) -> CompletionParams:
        return CompletionParams.json_mode(self.completion_max_tokens())

    @property
    @abstractmethod
    def role_definition(self) -> str:
        """Defines the assistant’s first-person role to guide behavior, tone, and domain scope."""

    @abstractmethod
    def structured_json_format(self) -> str:
        """Concrete JSON shape (middle section only). Wrapped by output_format."""

    @abstractmethod
    def build_messages(self) -> list[dict[str, Any]]: ...

    def output_format(self) -> str:
        schema = self.structured_json_format().strip()
        return f"{JSON_OUTPUT_RULES}\n\n{schema}"

    async def generate(
        self, model: str, llm: OpenAiChat
    ) -> tuple[str, list[dict[str, Any]], TokenUsage]:
        """Return assistant text, chat messages, and token usage for this completion.

        - **str** — raw assistant message content (expected JSON from the model).
        - **list** — same chat ``messages`` list sent to the API (for corrective retries).
        - **TokenUsage** — counts from this response (see :mod:`app.integrations.openai.token_usage`).
        """
        messages = self.build_messages()
        outcome = await llm.complete(model, messages, self._chat_completion)
        return outcome.text, messages, outcome.token_usage

    def _system_prompt(
        self,
        context: str = "",
        requirements: str = "",
        guidelines: str = "",
        examples: str = "",
        chain_of_thought: str = "",
    ) -> str:
        """Build the system message from ordered sections; optional blocks skip empty bodies after strip."""
        raw_bodies: dict[str, str] = {
            "role": self.role_definition,
            "guidelines": guidelines,
            "context": context,
            "requirements": requirements,
            "examples": examples,
            "chain_of_thought": chain_of_thought,
            "output_format": self.output_format(),
        }
        sections: list[str] = []
        for field, heading, always_emit in self._SYSTEM_SECTIONS:
            body = raw_bodies[field].strip()
            if not always_emit and not body:
                continue
            sections.append(f"# {heading}\n{body}")
        return "\n\n".join(sections)


__all__ = ["LlmJsonPrompter"]
