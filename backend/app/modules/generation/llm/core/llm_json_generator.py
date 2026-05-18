from typing import Generic, TypeVar

from pydantic import BaseModel

from app.modules.generation.services.parser import LlmJsonParser
from app.modules.generation.services.prompter import LlmJsonPrompter

TJsonModel = TypeVar("TJsonModel", bound=BaseModel)


class LlmJsonGenerator(
    LlmJsonPrompter, LlmJsonParser[TJsonModel], Generic[TJsonModel]
): ...
