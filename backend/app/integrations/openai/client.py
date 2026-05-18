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


def _token_usage_from_api_usage(response_usage: object | None) -> dict[str, int]:
    """Normalize OpenAI-style ``usage`` into prompt/completion token counts."""

    if response_usage is None:
        return {"prompt_tokens": 0, "completion_tokens": 0}
    pt = getattr(response_usage, "prompt_tokens", None)
    ct = getattr(response_usage, "completion_tokens", None)
    return {
        "prompt_tokens": max(0, int(pt)) if pt is not None else 0,
        "completion_tokens": max(0, int(ct)) if ct is not None else 0,
    }


@dataclass(frozen=True)
class CompletionResult:
    """Assistant text and normalized token usage from one chat completion."""

    text: str
    token_usage: dict[str, int]


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
        raw_usage = getattr(response, "usage", None)
        token_usage = _token_usage_from_api_usage(raw_usage)
        return CompletionResult(text=text, token_usage=token_usage)
