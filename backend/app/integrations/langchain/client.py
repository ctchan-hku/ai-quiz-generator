import httpx
from langchain_openai import ChatOpenAI

from app.config import settings
from app.integrations.langchain.constants import (
    OPENAI_HTTP_TIMEOUT_SECONDS,
)


def _llm_http_timeout() -> httpx.Timeout:
    timeout = OPENAI_HTTP_TIMEOUT_SECONDS
    connect_sec = min(30.0, timeout)
    return httpx.Timeout(
        connect=connect_sec,
        read=timeout,
        write=timeout,
        pool=timeout,
    )


def create_chat_model(model_id: str) -> ChatOpenAI:
    return ChatOpenAI(
        model=model_id,
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url,
        timeout=_llm_http_timeout(),
        temperature=0.0,
    )


__all__ = ["create_chat_model"]
