import json
import re
from typing import Any

from pydantic import ValidationError

PARSE_RECOVERABLE: tuple[type[Exception], ...] = (
    json.JSONDecodeError,
    ValidationError,
    ValueError,
)

PARSE_CORRECTIVE = (
    "That response was invalid JSON or failed schema validation. "
    "Follow the JSON shape required by the conversation above, with no extra text."
)

PARSE_RETRY_FAILURE_DETAIL = "LLM returned invalid data after retry"
PARSE_LLM_TOP_LEVEL_MUST_BE_OBJECT = "LLM output must be a JSON object"


def strip_fences(text: str) -> str:
    s = text.strip()
    if s.startswith("```"):
        s = re.sub(r"^```(?:json)?\s*", "", s, count=1, flags=re.IGNORECASE)
        s = re.sub(r"\s*```\s*$", "", s, count=1)
    return s.strip()


def _brace_balanced_object_slice(text: str, open_idx: int) -> str | None:
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


def parse_payload(raw: str, model_cls: type) -> Any:
    payload = parse_llm_json_object(raw)
    if not isinstance(payload, dict):
        raise ValueError(PARSE_LLM_TOP_LEVEL_MUST_BE_OBJECT)
    return model_cls.model_validate(payload)
