from pydantic import BaseModel, ConfigDict, Field

from app.modules.generation.models.mc_question import MultipleChoiceQuestion


class TestResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    questions: list[MultipleChoiceQuestion]
    model_used: str
    cost_usd: float = Field(ge=0)


class QuestionResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    question: MultipleChoiceQuestion
    cost_usd: float = Field(ge=0)
