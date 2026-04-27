"""Opt-in logging of full chat `messages` sent to the LLM (for debugging prompts)."""

import json
import logging
from typing import Any

from app.config import settings

logger = logging.getLogger(__name__)


def log_full_chat_messages(messages: list[dict[str, Any]], label: str) -> None:
    if not settings.log_full_llm_prompt:
        return
    try:
        text = json.dumps(messages, ensure_ascii=False, indent=2)
    except (TypeError, ValueError):
        text = repr(messages)
    logger.info("LLM chat completion messages [%s]:\n%s", label, text)
