from langchain_openai import ChatOpenAI

from app.config import settings
from app.integrations.openai._timeouts import get_timeout


def create_chat_model(model_id: str) -> ChatOpenAI:
    return ChatOpenAI(
        model=model_id,
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url,
        timeout=get_timeout(),
        temperature=0.0,
    )


__all__ = ["create_chat_model"]
