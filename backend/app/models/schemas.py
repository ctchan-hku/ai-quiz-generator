"""Quiz envelope models — each question row uses ``MultipleChoiceQuestion`` from ``mc_question``."""

from typing import Literal

from pydantic import BaseModel, ConfigDict

from app.models.mc_question import MultipleChoiceQuestion


class Quiz(BaseModel):    questions: list[MultipleChoiceQuestion]


class QuizResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    questions: list[MultipleChoiceQuestion]
    model_used: str
    source: Literal["topic", "file"]
    truncated: bool = False
