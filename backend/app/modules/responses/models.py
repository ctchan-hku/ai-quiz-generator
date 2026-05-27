from pydantic import BaseModel, ConfigDict, Field


class SpecificationItem(BaseModel):
    label: str
    value: int | float


class ResponseNrl(BaseModel):
    specification: list[SpecificationItem]


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
