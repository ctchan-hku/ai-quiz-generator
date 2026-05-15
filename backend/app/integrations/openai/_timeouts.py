"""HTTP client timeouts for OpenAI-compatible APIs (read-heavy chat completions)."""

import httpx

from app.config import settings


def get_timeout() -> httpx.Timeout:
    """Return timeouts for ``AsyncOpenAI``.

    The v2 answer step can request a large completion; slow providers may need a
    longer **read** window than connect. When ``OPENAI_HTTP_READ_TIMEOUT`` is unset,
    all phases use ``OPENAI_HTTP_TIMEOUT`` (same behaviour as a single float).
    """

    base = settings.openai_http_timeout_seconds
    read_sec = settings.openai_http_read_timeout_seconds or base
    connect_sec = min(30.0, base)
    return httpx.Timeout(
        connect=connect_sec,
        read=read_sec,
        write=read_sec,
        pool=read_sec,
    )
