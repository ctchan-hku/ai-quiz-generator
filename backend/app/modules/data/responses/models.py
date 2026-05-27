from pydantic import BaseModel, ConfigDict, Field


class AnswerContent(BaseModel):
    label: str | None = None
    value: int | float


class AnswerItem(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    question_id: str = Field(default="", alias="questionId")
    content: AnswerContent | None = None


class ResponseRecord(BaseModel):
    id: str
    answers: list[AnswerItem] = Field(default_factory=list)


class ResponseListResponse(BaseModel):
    responses: list[ResponseRecord] = Field(default_factory=list)
