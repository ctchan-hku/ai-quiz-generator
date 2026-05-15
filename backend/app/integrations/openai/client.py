"""OpenAI-compatible HTTP client and chat completions (primary integration surface)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from openai import AsyncOpenAI

from app.config import settings
from app.integrations.openai._timeouts import get_timeout

MAX_COMPLETION_TOKENS = 4096
MAX_DEBUG_COMPLETION_TOKENS = 64
DEBUG_COMPLETION_TEMPERATURE = 0.7


@dataclass(frozen=True)
class CompletionParams:
    """Keyword arguments for ``client.chat.completions.create`` (excluding model/messages)."""

    temperature: float
    max_tokens: int
    response_format: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }
        if self.response_format is not None:
            out["response_format"] = self.response_format
        return out

    @classmethod
    def json_mode(cls, max_tokens: int) -> CompletionParams:
        return cls(
            temperature=0.0,
            max_tokens=max_tokens,
            response_format={"type": "json_object"},
        )

    @classmethod
    def plain(cls, *, max_tokens: int, temperature: float) -> CompletionParams:
        return cls(
            temperature=temperature,
            max_tokens=max_tokens,
            response_format=None,
        )


@dataclass(frozen=True)
class CompletionResult:
    """Assistant text and usage from one chat completion response."""

    text: str
    usage: Any


@dataclass(frozen=True, slots=True)
class OpenAiChat:
    """OpenAI chat: bound HTTP client plus a single completion entry point."""

    client: AsyncOpenAI

    @classmethod
    def create(cls) -> OpenAiChat:
        client = AsyncOpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url,
            timeout=get_timeout(),
        )
        return cls(client=client)

    async def complete(
        self,
        model: str,
        messages: list,
        params: CompletionParams,
    ) -> CompletionResult:
        response = await self.client.chat.completions.create(
            model=model,
            messages=messages,
            **params.to_dict(),
        )
        text = response.choices[0].message.content or ""
        usage = getattr(response, "usage", None)
        return CompletionResult(text=text, usage=usage)
