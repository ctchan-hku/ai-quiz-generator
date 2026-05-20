from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class CourseGroupSummary(BaseModel):
    id: str
    name: str


class CourseGroupListResponse(BaseModel):
    course_groups: list[CourseGroupSummary] = Field(default_factory=list)


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


class TestRecord(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    __test__ = False

    id: str
    name: str
    questions: list[Any] = Field(default_factory=list)
    grade_cutoff: list[Any] = Field(default_factory=list)


class TestListResponse(BaseModel):
    __test__ = False

    tests: list[TestRecord] = Field(default_factory=list)


class AnswerContent(BaseModel):
    label: str | None = None
    value: int | float


class AnswerItem(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    question_id: str = Field(default="", alias="questionId")
    content: AnswerContent | None = None


class LabelCount(BaseModel):
    label: str
    count: int


class QuestionMetric(BaseModel):
    question_id: str
    label_counts: list[LabelCount] = Field(default_factory=list)
    difficulty_index: float | None = None
    discrimination_index: float | None = None


class QuestionMetricsResponse(BaseModel):
    questions: list[QuestionMetric] = Field(default_factory=list)


class ResponseRecord(BaseModel):
    id: str
    answers: list[AnswerItem] = Field(default_factory=list)


class ResponseListResponse(BaseModel):
    responses: list[ResponseRecord] = Field(default_factory=list)
