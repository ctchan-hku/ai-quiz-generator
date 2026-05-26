from __future__ import annotations

from collections.abc import Callable
from typing import Annotated

from fastapi import Depends
from langchain_core.language_models.chat_models import BaseChatModel

from app.integrations.langchain.client import create_chat_model


def get_chat_model_factory() -> Callable[[str], BaseChatModel]:
    return create_chat_model


ChatModelFactory = Annotated[
    Callable[[str], BaseChatModel],
    Depends(get_chat_model_factory),
]


def bind_chat_model(
    factory: Callable[[str], BaseChatModel],
    model_id: str,
) -> BaseChatModel:
    return factory(model_id)


__all__ = ["ChatModelFactory", "bind_chat_model", "get_chat_model_factory"]
