from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TokenUsage:
    prompt_tokens: int = 0
    completion_tokens: int = 0

    @classmethod
    def from_raw(cls, usage: object | None) -> TokenUsage:

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
