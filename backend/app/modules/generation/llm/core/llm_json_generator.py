"""Mixin for LLM steps that prompt for JSON and validate it into a typed :class:`~pydantic.BaseModel`."""

from typing import Generic, TypeVar

from pydantic import BaseModel

from app.modules.generation.services.parser import LlmJsonParser
from app.modules.generation.services.prompter import LlmJsonPrompter

TJsonModel = TypeVar("TJsonModel", bound=BaseModel)


class LlmJsonGenerator(LlmJsonPrompter, LlmJsonParser[TJsonModel], Generic[TJsonModel]):
    """Subclasses implement prompts + schema; ``generate`` / ``parse_with_retry`` produce one JSON object per call."""
