"""HTTP response bodies for `POST /api/generate/quiz` and `POST /api/generate/question`."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.modules.generation.models.mc_question import MultipleChoiceQuestion


class QuizResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    questions: list[MultipleChoiceQuestion]
    model_used: str
    source: Literal["topic", "file"]
    truncated: bool = False
    cost_usd: float = Field(ge=0)


class QuestionGenerateResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    question: MultipleChoiceQuestion
    cost_usd: float = Field(ge=0)
