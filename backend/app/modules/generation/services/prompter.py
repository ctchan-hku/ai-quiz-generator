"""Structured prompts and JSON-mode chat completion for LLM JSON responses."""

from abc import ABC, abstractmethod
from typing import Any, ClassVar

from openai import AsyncOpenAI

from app.modules.generation.models import TokenUsage, add_usage
from app.modules.generation.config.prompts import JSON_OUTPUT_RULES

MAX_COMPLETION_TOKENS = 4096
COMPLETION_TEMPERATURE = 0

CHAT_COMPLETION_KWARGS: dict[str, Any] = {
    "response_format": {"type": "json_object"},
    "temperature": COMPLETION_TEMPERATURE,
    "max_tokens": MAX_COMPLETION_TOKENS,
}


async def complete_chat(
    client: AsyncOpenAI,
    model: str,
    messages: list,
    *,
    completion: dict[str, Any],
) -> tuple[str, list[dict[str, Any]], TokenUsage]:
    """Return assistant text, the same ``messages`` list (for retries), and token usage from the response."""
    response = await client.chat.completions.create(
        messages=messages,
        model=model,
        **completion,
    )
    raw = response.choices[0].message.content or ""
    usage = add_usage(TokenUsage(), getattr(response, "usage", None))
    return raw, messages, usage


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

    @property
    def _chat_completion(self) -> dict[str, Any]:
        return CHAT_COMPLETION_KWARGS

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
        self, model: str, client: AsyncOpenAI
    ) -> tuple[str, list[dict[str, Any]], TokenUsage]:
        """Return assistant text, chat messages, and usage for this completion.

        - **str** — raw assistant message content (expected JSON from the model).
        - **list** — same chat ``messages`` list sent to the API (for corrective retries).
        - **TokenUsage** — ``prompt_tokens`` / ``completion_tokens`` from this response.
        """
        messages = self.build_messages()
        return await complete_chat(
            client,
            model,
            messages,
            completion=self._chat_completion,
        )

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
