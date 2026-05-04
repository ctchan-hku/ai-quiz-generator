import json
import re
from dataclasses import dataclass
from typing import Any, Callable, TypeVar

from fastapi import HTTPException
from openai import AsyncOpenAI
from pydantic import ValidationError

from app.models.token_usage import TokenUsage, add_usage
from app.services.llm.debug_log import log_full_chat_messages

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


def strip_fences(text: str) -> str:
    s = text.strip()
    if s.startswith("```"):
        s = re.sub(r"^```(?:json)?\s*", "", s, count=1, flags=re.IGNORECASE)
        s = re.sub(r"\s*```\s*$", "", s, count=1)
    return s.strip()


@dataclass(frozen=True, slots=True)
class LlmParseRetrySpec:
    """What to retry and how to log / respond when a second parse still fails."""

    corrective: str
    log_label: str
    error_msg: str
    recoverable: tuple[type[Exception], ...] = PARSE_RECOVERABLE


def make_llm_parse_retry_spec(*, class_name: str) -> LlmParseRetrySpec:
    """Retry spec keyed by task class name (log label and error message)."""
    return LlmParseRetrySpec(
        corrective=PARSE_CORRECTIVE,
        log_label=f"{RETRY_LOG_PREFIX}_{class_name}",
        error_msg=f"LLM returned invalid data after retry ({class_name})",
    )


async def parse_llm_with_retry(
    raw: str,
    client: AsyncOpenAI,
    messages: list,
    *,
    parse: Callable[[str], T],
    spec: LlmParseRetrySpec,
    chat_completion_kwargs: dict[str, Any],
    initial_usage: TokenUsage | None = None,
) -> tuple[T, TokenUsage]:
    total = TokenUsage() if initial_usage is None else initial_usage.model_copy()
    try:
        return parse(raw), total
    except Exception as e:
        if not isinstance(e, spec.recoverable):
            raise
        corrective_messages = list(messages) + [
            {"role": "assistant", "content": raw},
            {"role": "user", "content": spec.corrective},
        ]
        log_full_chat_messages(corrective_messages, spec.log_label)
        retry = await client.chat.completions.create(
            messages=corrective_messages,
            **chat_completion_kwargs,
        )
        retry_raw = retry.choices[0].message.content or ""
        total = add_usage(total, getattr(retry, "usage", None))
        try:
            return parse(retry_raw), total
        except Exception as exc:
            if not isinstance(exc, spec.recoverable):
                raise
            raise HTTPException(status_code=502, detail=spec.error_msg) from exc
