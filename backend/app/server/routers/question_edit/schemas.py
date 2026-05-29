from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.features.generation.models import MultipleChoiceQuestion


class QuestionEditRequest(BaseModel):
    model: str
    topic: str = Field(default="", max_length=2000)
    question: MultipleChoiceQuestion
    comment: str = ""

    @field_validator("topic")
    @classmethod
    def strip_topic(cls, v: object) -> str:
        if not isinstance(v, str):
            raise TypeError("topic must be a string")
        return v.strip()

    @field_validator("comment", mode="before")
    @classmethod
    def normalize_comment(cls, v: object) -> str:
        if v is None:
            return ""
        if not isinstance(v, str):
            raise TypeError("comment must be a string")
        s = v.strip()
        if len(s) > 2000:
            raise ValueError("comment must be at most 2000 characters after trim")
        return s


class QuestionEditResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    question: MultipleChoiceQuestion
    cost_usd: float = Field(ge=0)
