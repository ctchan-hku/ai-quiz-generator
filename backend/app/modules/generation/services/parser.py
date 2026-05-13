"""LLM JSON parsing: fences, retry helpers, and typed parse base."""

import json
import re
from typing import Any, Generic, TypeVar

from fastapi import HTTPException
from openai import AsyncOpenAI
from pydantic import BaseModel, ValidationError

from app.modules.generation.helpers.logging import log_full_llm_chat
from app.modules.generation.models import TokenUsage, add_usage
from app.modules.generation.services.prompter import CHAT_COMPLETION_KWARGS

T = TypeVar("T", bound=BaseModel)

PARSE_RECOVERABLE: tuple[type[Exception], ...] = (
    json.JSONDecodeError,
    ValidationError,
    ValueError,
)

PARSE_CORRECTIVE = "That response was invalid JSON or failed schema validation. Follow the JSON shape required by the conversation above, with no extra text."

PARSE_RETRY_FAILURE_DETAIL = "LLM returned invalid data after retry"
PARSE_LLM_TOP_LEVEL_MUST_BE_OBJECT = "LLM output must be a JSON object"


def strip_fences(text: str) -> str:
    s = text.strip()
    if s.startswith("```"):
        s = re.sub(r"^```(?:json)?\s*", "", s, count=1, flags=re.IGNORECASE)
        s = re.sub(r"\s*```\s*$", "", s, count=1)
    return s.strip()


def _brace_balanced_object_slice(text: str, open_idx: int) -> str | None:
    """Slice ``text[open_idx:…]`` as one balanced JSON object, respecting quoted strings."""

    if open_idx >= len(text) or text[open_idx] != "{":
        return None
    depth = 0
    in_string = False
    escape = False
    i = open_idx
    n = len(text)
    while i < n:
        ch = text[i]
        if in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
        else:
            if ch == '"':
                in_string = True
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return text[open_idx : i + 1]
        i += 1
    return None


def parse_llm_json_object(raw: str) -> Any:
    """Parse JSON from model output: whole message, fenced body, or first embedded object."""

    if raw is None:
        raise json.JSONDecodeError("Empty LLM message", "", 0)

    stripped = strip_fences(raw.strip())
    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        pass

    for idx, ch in enumerate(raw):
        if ch != "{":
            continue
        fragment = _brace_balanced_object_slice(raw, idx)
        if fragment is None:
            continue
        try:
            return json.loads(fragment)
        except json.JSONDecodeError:
            continue

    raise json.JSONDecodeError(
        "Could not parse a JSON object from LLM output",
        raw,
        0,
    )


class LlmJsonParser(Generic[T]):
    """Read what the model returned and build a typed, validated result.

    Subclasses implement parse to unpack the reply and check it fits the schema.
    If that fails, parse_with_retry asks the model for a corrected reply and tries again.
    """

    def _chat_completion_for_retry(
        self, chat_completion: dict[str, Any] | None
    ) -> dict[str, Any]:
        if chat_completion is not None:
            return chat_completion
        descriptor = getattr(type(self), "_chat_completion", None)
        if isinstance(descriptor, property):
            return descriptor.fget(self)
        return CHAT_COMPLETION_KWARGS

    def parse(self, raw: str) -> T:
        payload = parse_llm_json_object(raw)
        if not isinstance(payload, dict):
            raise ValueError(PARSE_LLM_TOP_LEVEL_MUST_BE_OBJECT)
        return self.parse_response_model.model_validate(payload)

    async def parse_with_retry(
        self,
        raw: str,
        client: AsyncOpenAI,
        messages: list,
        *,
        model: str,
        chat_completion: dict[str, Any] | None = None,
        initial_usage: TokenUsage | None = None,
    ) -> tuple[T, TokenUsage]:
        total = TokenUsage() if initial_usage is None else initial_usage.model_copy()
        completion_kw = self._chat_completion_for_retry(chat_completion)
        class_label = type(self).__name__
        try:
            parsed = self.parse(raw)
            log_full_llm_chat(
                label=class_label,
                messages=[
                    *messages,
                    {"role": "assistant", "content": raw},
                ],
                model=model,
            )
            return parsed, total
        except Exception as e:
            if not isinstance(e, PARSE_RECOVERABLE):
                raise
            corrective_messages = list(messages) + [
                {"role": "assistant", "content": raw},
                {"role": "user", "content": PARSE_CORRECTIVE},
            ]
            retry = await client.chat.completions.create(
                messages=corrective_messages,
                model=model,
                **completion_kw,
            )
            total = add_usage(total, getattr(retry, "usage", None))
            retry_raw = retry.choices[0].message.content or ""
            retry_messages = [
                *corrective_messages,
                {"role": "assistant", "content": retry_raw},
            ]
            log_full_llm_chat(
                label=f"{class_label} · retry",
                messages=retry_messages,
                model=model,
            )
            try:
                parsed = self.parse(retry_raw)
            except Exception as exc:
                if not isinstance(exc, PARSE_RECOVERABLE):
                    raise
                raise HTTPException(
                    status_code=502, detail=PARSE_RETRY_FAILURE_DETAIL
                ) from exc
            return parsed, total
