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
    """Build JSON-mode system prompts and run one chat completion."""

    _SPECIAL_SECTION_KEYS: ClassVar[frozenset[str]] = frozenset(
        {"role", "output_format"},
    )

    _SYSTEM_SECTIONS: ClassVar[tuple[tuple[str, str], ...]] = (
        ("role", "Role"),
        ("guidelines", "Guidelines"),
        ("context", "Context"),
        ("requirements", "Requirements"),
        ("examples", "Examples"),
        ("chain_of_thought", "Chain of Thought"),
        ("output_format", "Output Format"),
    )

    def completion_max_tokens(self) -> int:
        return MAX_COMPLETION_TOKENS

    @property
    def _chat_completion(self) -> CompletionParams:
        return CompletionParams.json_mode(self.completion_max_tokens())

    @property
    @abstractmethod
    def role_definition(self) -> str:
        ...

    @abstractmethod
    def structured_json_format(self) -> str:
        """Middle of # Output Format: JSON example only (rules wrapper is separate)."""
        ...

    @abstractmethod
    def build_messages(self) -> list[dict[str, Any]]: ...

    def output_format(self) -> str:
        schema = self.structured_json_format().strip()
        return f"{JSON_OUTPUT_RULES}\n\n{schema}"

    async def generate(
        self, model: str, llm: OpenAiChat
    ) -> tuple[str, list[dict[str, Any]], TokenUsage]:
        """Assistant text, request ``messages``, and usage for this call."""
        messages = self.build_messages()
        outcome = await llm.complete(model, messages, self._chat_completion)
        return outcome.text, messages, outcome.token_usage

    def _system_prompt(self, **sections: str) -> str:
        """Build ``#`` sections in order; skip empty bodies. Unknown ``**sections`` keys raise."""
        variable_keys = tuple(
            key
            for key, _ in self._SYSTEM_SECTIONS
            if key not in self._SPECIAL_SECTION_KEYS
        )
        allowed = frozenset(variable_keys)
        unknown = frozenset(sections) - allowed
        if unknown:
            raise TypeError(
                f"_system_prompt: unknown keys {sorted(unknown)!r}; "
                f"allowed {sorted(allowed)!r}",
            )

        raw_bodies: dict[str, str] = {
            "role": self.role_definition,
            "output_format": self.output_format(),
        }
        for key in variable_keys:
            raw_bodies[key] = sections.get(key, "")

        parts: list[str] = []
        for field, heading in self._SYSTEM_SECTIONS:
            body = raw_bodies[field].strip()
            if not body:
                continue
            parts.append(f"# {heading}\n{body}")
        return "\n\n".join(parts)


__all__ = ["LlmJsonPrompter"]
