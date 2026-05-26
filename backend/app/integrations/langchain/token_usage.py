from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import LLMResult


@dataclass
class TokenUsage:
    prompt_tokens: int = 0
    completion_tokens: int = 0

    def __iadd__(self, delta: TokenUsage) -> TokenUsage:
        self.prompt_tokens += delta.prompt_tokens
        self.completion_tokens += delta.completion_tokens
        return self


class TokenUsageCallbackHandler(BaseCallbackHandler):
    def __init__(self) -> None:
        self.usage = TokenUsage()

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        llm_output = response.llm_output
        if not llm_output:
            return
        token_usage = llm_output.get("token_usage")
        if not token_usage:
            return
        self.usage += TokenUsage(
            prompt_tokens=int(token_usage.get("prompt_tokens", 0)),
            completion_tokens=int(token_usage.get("completion_tokens", 0)),
        )


__all__ = ["TokenUsage", "TokenUsageCallbackHandler"]
