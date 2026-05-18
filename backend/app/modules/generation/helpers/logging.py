import json
import logging
from datetime import datetime
from typing import Any

from app.config import settings

logger = logging.getLogger(__name__)


def _content_as_text(content: Any) -> str:
    if content is None:
        return "(empty)"
    if isinstance(content, str):
        return content
    return json.dumps(content, ensure_ascii=False, indent=2)


CHAT_LOG_DIVIDER = "=" * 88


def _format_messages_readable(messages: list[dict[str, Any]]) -> str:
    parts: list[str] = []
    for i, m in enumerate(messages):
        role = m.get("role", "?")
        header = f"── message {i + 1} · role={role} ──"
        body = _content_as_text(m.get("content"))
        extra = {k: v for k, v in m.items() if k not in ("role", "content")}
        block = f"{header}\n{body}"
        if extra:
            block += (
                f"\n— other fields —\n{json.dumps(extra, ensure_ascii=False, indent=2)}"
            )
        parts.append(block)
    return "\n\n".join(parts)


def log_full_llm_chat(
    *,
    label: str,
    messages: list[dict[str, Any]],
    model: str = "",
) -> None:
    """Full chat dump to logs when ``settings.log_full_llm_prompt`` is on."""
    if not settings.log_full_llm_prompt:
        return
    try:
        body = _format_messages_readable(messages)
    except Exception:
        body = repr(messages)

    timestamp = datetime.now().isoformat()

    label_line = f"=== [{label} · {model}] Chat Completion @ {timestamp} ==="
    logger.info(
        "\n%s\n%s\n%s\n%s",
        CHAT_LOG_DIVIDER,
        label_line,
        body,
        CHAT_LOG_DIVIDER,
    )
