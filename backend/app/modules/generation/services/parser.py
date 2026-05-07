"""LLM JSON parsing: fences, retry helpers, and typed parse base."""

import json
import re
from abc import ABC, abstractmethod
from typing import Any, Callable, Generic, TypeVar

from fastapi import HTTPException
from openai import AsyncOpenAI
from pydantic import ValidationError

from app.models.token_usage import TokenUsage, add_usage
from app.modules.generation.helpers.logging import log_full_chat_messages

T = TypeVar("T")

PARSE_RECOVERABLE: tuple[type[Exception], ...] = (
    json.JSONDecodeError,
    ValidationError,
    ValueError,
)

PARSE_CORRECTIVE = (
    "That response was invalid JSON or failed schema validation. Follow the JSON shape required by the conversation above, with no extra text."
)

RETRY_LOG_PREFIX = "parse_with_retry"
PARSE_RETRY_FAILURE_DETAIL = "LLM returned invalid data after retry"


def strip_fences(text: str) -> str:
    s = text.strip()
    if s.startswith("```"):
        s = re.sub(r"^```(?:json)?\s*", "", s, count=1, flags=re.IGNORECASE)
        s = re.sub(r"\s*```\s*$", "", s, count=1)
    return s.strip()


async def parse_llm_with_retry(
    raw: str,
    client: AsyncOpenAI,
    messages: list,
    *,
    parse: Callable[[str], T],
    chat_completion_kwargs: dict[str, Any],
    initial_usage: TokenUsage | None = None,
) -> tuple[T, TokenUsage]:
    total = TokenUsage() if initial_usage is None else initial_usage.model_copy()
    try:
        return parse(raw), total
    except Exception as e:
        if not isinstance(e, PARSE_RECOVERABLE):
            raise
        corrective_messages = list(messages) + [
            {"role": "assistant", "content": raw},
            {"role": "user", "content": PARSE_CORRECTIVE},
        ]
        log_full_chat_messages(corrective_messages, RETRY_LOG_PREFIX)
        retry = await client.chat.completions.create(
            messages=corrective_messages,
            **chat_completion_kwargs,
        )
        total = add_usage(total, getattr(retry, "usage", None))
        try:
            return parse(retry.choices[0].message.content or ""), total
        except Exception as exc:
            if not isinstance(exc, PARSE_RECOVERABLE):
                raise
            raise HTTPException(status_code=502, detail=PARSE_RETRY_FAILURE_DETAIL) from exc


class BaseLlmJsonParse(ABC, Generic[T]):
    """Read what the model returned and build a typed, validated result.

    Subclasses implement parse to unpack the reply and check it fits the schema.
    If that fails, parse_with_retry asks the model for a corrected reply and tries again.
    """

    @abstractmethod
    def parse(self, raw: str) -> T:
        """Turn one assistant message string into the validated result object."""

    async def parse_with_retry(
        self,
        raw: str,
        client: AsyncOpenAI,
        messages: list,
        *,
        chat_completion_kwargs: dict[str, Any],
        initial_usage: TokenUsage | None = None,
    ) -> tuple[T, TokenUsage]:
        return await parse_llm_with_retry(
            raw,
            client,
            messages,
            parse=self.parse,
            chat_completion_kwargs=chat_completion_kwargs,
            initial_usage=initial_usage,
        )
