from pydantic import BaseModel


class SpecificationItem(BaseModel):
    label: str
    value: int | float


class ResponseNrl(BaseModel):
    specification: list[SpecificationItem]


class QuestionRecord(BaseModel):
    id: str
    prompt: str | None = None
    type: str | None = None
    response_nrl: ResponseNrl
