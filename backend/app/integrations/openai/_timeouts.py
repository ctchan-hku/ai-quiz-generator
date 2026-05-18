import httpx

from app.config import settings


def get_timeout() -> httpx.Timeout:
    """How long HTTP calls to the AI provider may wait.

    Slow models can need a longer *read* time than *connect*. If the read timeout env var
    is unset, every phase uses the main timeout value (same as giving httpx one number).
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
