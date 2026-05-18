"""Shared pipeline construction and per-step ``generate`` → ``parse_with_retry`` orchestration."""

from __future__ import annotations

from typing import TypeVar

from pydantic import BaseModel

from app.integrations.openai.client import OpenAiChat
from app.modules.generation.llm.core.llm_json_generator import LlmJsonGenerator

TStep = TypeVar("TStep", bound=BaseModel)


class BasePipeline:
    """Base pipeline applicable to both question generation and quiz generation."""

    def __init__(self) -> None:
        self.token_usage: dict[str, int] = {"prompt_tokens": 0, "completion_tokens": 0}

    async def _run_generator_step(
        self,
        generator: LlmJsonGenerator[TStep],
        model: str,
        llm: OpenAiChat,
    ) -> TStep:
        raw, messages, gen_usage = await generator.generate(model, llm)
        self.token_usage["prompt_tokens"] += gen_usage["prompt_tokens"]
        self.token_usage["completion_tokens"] += gen_usage["completion_tokens"]

        parsed, retry_usage = await generator.parse_with_retry(
            raw,
            llm,
            messages,
            model=model,
        )
        self.token_usage["prompt_tokens"] += retry_usage["prompt_tokens"]
        self.token_usage["completion_tokens"] += retry_usage["completion_tokens"]

        return parsed
