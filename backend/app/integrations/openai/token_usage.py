"""Prompt/completion token counts from OpenAI-style chat completion responses."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TokenUsage:
    """Single completion or accumulated usage; supports ``total += delta``."""

    prompt_tokens: int = 0
    completion_tokens: int = 0

    @classmethod
    def from_response_usage(cls, usage: object | None) -> TokenUsage:
        """Build from an SDK ``completion.usage`` object (or compatible duck type)."""

        if usage is None:
            return cls()
        pt = getattr(usage, "prompt_tokens", None)
        ct = getattr(usage, "completion_tokens", None)
        return cls(
            prompt_tokens=max(0, int(pt)) if pt is not None else 0,
            completion_tokens=max(0, int(ct)) if ct is not None else 0,
        )

    def __iadd__(self, delta: TokenUsage) -> TokenUsage:
        self.prompt_tokens += delta.prompt_tokens
        self.completion_tokens += delta.completion_tokens
        return self
