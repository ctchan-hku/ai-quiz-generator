import json
import re
from typing import Any

from fastapi import HTTPException
from openai import AsyncOpenAI
from pydantic import ValidationError

from app.models.schemas import QuizSchema


def _strip_fences(text: str) -> str:
    s = text.strip()
    if s.startswith("```"):
        s = re.sub(r"^```(?:json)?\s*", "", s, count=1, flags=re.IGNORECASE)
        s = re.sub(r"\s*```\s*$", "", s, count=1)
    return s.strip()


def _parse(raw: str) -> QuizSchema:
    stripped = _strip_fences(raw)
    result = json.loads(stripped)
    if isinstance(result, list):
        data = {"questions": result}
    elif isinstance(result, dict) and "questions" in result:
        data = result
    else:
        raise ValueError("Unexpected LLM output shape")
    return QuizSchema.model_validate(data)


async def parse_with_retry(
    raw: str,
    client: AsyncOpenAI,
    messages: list,
    *,
    chat_completion_kwargs: dict[str, Any],
) -> QuizSchema:
    try:
        return _parse(raw)
    except (json.JSONDecodeError, ValidationError):
        corrective_messages = list(messages) + [
            {"role": "assistant", "content": raw},
            {
                "role": "user",
                "content": (
                    "That response was invalid JSON or failed schema validation. "
                    "Return ONLY the corrected JSON array, no other text."
                ),
            },
        ]
        retry = await client.chat.completions.create(
            messages=corrective_messages,
            **chat_completion_kwargs,
        )
        retry_raw = retry.choices[0].message.content or ""
        try:
            return _parse(retry_raw)
        except (json.JSONDecodeError, ValidationError) as exc:
            raise HTTPException(
                status_code=502,
                detail="LLM returned invalid quiz data after retry",
            ) from exc
