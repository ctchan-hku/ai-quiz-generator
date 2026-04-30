"""OpenAI client, shared completion defaults, and one `chat.completions.create` with logging."""

from typing import Any

from openai import AsyncOpenAI

from app.config import settings
from app.services.llm.debug_log import log_full_chat_messages

MAX_COMPLETION_TOKENS = 4096
COMPLETION_TEMPERATURE = 0

CHAT_COMPLETION_KWARGS: dict[str, Any] = {
    "response_format": {"type": "json_object"},
    "temperature": COMPLETION_TEMPERATURE,
    "max_tokens": MAX_COMPLETION_TOKENS,
}


def get_llm_client() -> AsyncOpenAI:
    return AsyncOpenAI(
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url,
        timeout=55,
    )


async def complete_chat(
    client: AsyncOpenAI,
    model: str,
    messages: list,
    *,
    log_label: str,
    completion: dict[str, Any],
) -> tuple[str, list]:
    """Run one `chat.completions.create`; log messages; return assistant text and the same `messages` list."""
    log_full_chat_messages(messages, log_label)
    response = await client.chat.completions.create(
        messages=messages,
        model=model,
        **completion,
    )
    raw = response.choices[0].message.content or ""
    return raw, messages
