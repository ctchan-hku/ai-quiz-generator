import json
import re
from dataclasses import dataclass
from typing import Any, Callable, TypeVar

from fastapi import HTTPException
from openai import AsyncOpenAI
from pydantic import ValidationError

from app.llm_debug_log import log_full_chat_messages

T = TypeVar("T")

# Retried for both full-quiz and single-MCQ: bad JSON, schema mismatch, or wrong top-level JSON shape.
LLM_JSON_PARSE_RECOVERABLE: tuple[type[Exception], ...] = (
    json.JSONDecodeError,
    ValidationError,
    ValueError,
)

LLM_PARSE_CORRECTIVE_INTRO = (
    "That response was invalid JSON or failed schema validation. "
)

# Debug log label: f"{LLM_PARSE_WITH_RETRY_LOG_PREFIX}_{failure_noun}".
LLM_PARSE_WITH_RETRY_LOG_PREFIX = "parse_with_retry"


def _strip_fences(text: str) -> str:
    s = text.strip()
    if s.startswith("```"):
        s = re.sub(r"^```(?:json)?\s*", "", s, count=1, flags=re.IGNORECASE)
        s = re.sub(r"\s*```\s*$", "", s, count=1)
    return s.strip()


def load_llm_json_value(raw: str) -> Any:
    """Strip optional markdown fences and `json.loads` the assistant text."""
    return json.loads(_strip_fences(raw))


@dataclass(frozen=True, slots=True)
class LlmParseRetrySpec:
    """What to retry and how to log / respond when a second parse still fails."""

    corrective: str
    log_label: str
    detail_502: str
    recoverable: tuple[type[Exception], ...] = LLM_JSON_PARSE_RECOVERABLE


def make_llm_parse_retry_spec(
    *,
    follow_up: str,
    failure_noun: str,
) -> LlmParseRetrySpec:
    """Build a spec with `parse_with_retry_<failure_noun>` log label and `detail_502`."""
    return LlmParseRetrySpec(
        corrective=LLM_PARSE_CORRECTIVE_INTRO + follow_up,
        log_label=f"{LLM_PARSE_WITH_RETRY_LOG_PREFIX}_{failure_noun}",
        detail_502=f"LLM returned invalid {failure_noun} data after retry",
    )


async def parse_llm_with_retry(
    raw: str,
    client: AsyncOpenAI,
    messages: list,
    *,
    parse: Callable[[str], T],
    spec: LlmParseRetrySpec,
    chat_completion_kwargs: dict[str, Any],
) -> T:
    try:
        return parse(raw)
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
        try:
            return parse(retry_raw)
        except Exception as exc:
            if not isinstance(exc, spec.recoverable):
                raise
            raise HTTPException(status_code=502, detail=spec.detail_502) from exc
