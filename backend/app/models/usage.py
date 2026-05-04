"""Token counts from OpenAI-style completion responses."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class TokenUsage(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    prompt_tokens: int = 0
    completion_tokens: int = 0


def add_usage(acc: TokenUsage, response_usage: object | None) -> TokenUsage:
    if response_usage is None:
        return acc.model_copy()
    pt = getattr(response_usage, "prompt_tokens", None)
    ct = getattr(response_usage, "completion_tokens", None)
    delta_pt = max(0, int(pt)) if pt is not None else 0
    delta_ct = max(0, int(ct)) if ct is not None else 0
    return TokenUsage(
        prompt_tokens=acc.prompt_tokens + delta_pt,
        completion_tokens=acc.completion_tokens + delta_ct,
    )
