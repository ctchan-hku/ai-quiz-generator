"""One LLM step combining JSON-mode prompting (:class:`JsonResponsePrompter`) and typed parse (:class:`BaseLlmJsonParse`)."""

from typing import Generic, TypeVar

from pydantic import BaseModel

from app.modules.generation.services.parser import BaseLlmJsonParse
from app.modules.generation.services.prompter import JsonResponsePrompter

TJsonModel = TypeVar("TJsonModel", bound=BaseModel)


class JsonPrompterParseTask(JsonResponsePrompter, BaseLlmJsonParse[TJsonModel], Generic[TJsonModel]):
    """Concrete tasks subclass this instead of listing ``JsonResponsePrompter`` and ``BaseLlmJsonParse`` separately."""
