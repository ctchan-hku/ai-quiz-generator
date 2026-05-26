import httpx
from langchain_openai import ChatOpenAI

from app.config import settings


def _llm_http_timeout() -> httpx.Timeout:
    base = settings.openai_http_timeout_seconds
    read_sec = settings.openai_http_read_timeout_seconds or base
    connect_sec = min(30.0, base)
    return httpx.Timeout(
        connect=connect_sec,
        read=read_sec,
        write=read_sec,
        pool=read_sec,
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
