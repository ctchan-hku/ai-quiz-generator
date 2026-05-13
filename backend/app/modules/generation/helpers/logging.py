"""LLM-oriented logging (full prompt dumps and usage summaries; opt-in via settings)."""

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
    """Render each turn with real newlines (not JSON-escaped ``\\n`` inside strings)."""
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
    """Log a full transcript (system, user, and accepted assistant output) after validation.

    Only runs when ``settings.log_full_llm_prompt`` is enabled. Upper and lower borders
    separate consecutive dumps in log output.
    """
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


def _format_rate_usd_per_million(value: float | None) -> str:
    if value is None:
        return "missing"
    text = format(float(value), ".12g")
    return f"{text} USD / 1M tokens"


def _format_cost_usd(value: float) -> str:
    return format(float(value), ".12g")


def log_generate_usage(
    *,
    route: str,
    model_id: str,
    prompt_tokens: int,
    completion_tokens: int,
    cost_usd: float,
    rate_input_per_million: float | None,
    rate_output_per_million: float | None,
) -> None:
    """Log aggregated token counts and catalog-based cost estimate (no prompt content)."""

    lines = (
        "Generation usage",
        f"  route:                 {route}",
        f"  model_id:              {model_id}",
        f"  prompt_tokens:         {prompt_tokens}",
        f"  completion_tokens:     {completion_tokens}",
        "  catalog (USD per 1M tokens)",
        f"    input rate:           {_format_rate_usd_per_million(rate_input_per_million)}",
        f"    output rate:           {_format_rate_usd_per_million(rate_output_per_million)}",
        f"  estimated cost_usd:    {_format_cost_usd(cost_usd)}",
    )
    logger.info("\n".join(lines))
