from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class CourseGroupSummary(BaseModel):
    id: str
    name: str


class TestSummary(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    __test__ = False

    id: str
    name: str
    num_questions: int


class CourseGroupWithTests(BaseModel):
    id: str
    name: str
    tests: list[TestSummary] = Field(default_factory=list)


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


class OptionMetric(BaseModel):
    label: str
    selection_rate: float
    cohort_attraction: list[float] = Field(default_factory=list)
    effectiveness: float | None = None


class QuestionMetric(BaseModel):
    question_id: str
    options: list[OptionMetric] = Field(default_factory=list)
    difficulty_index: list[float] = Field(default_factory=list)
    discrimination_index: list[float] = Field(default_factory=list)


class QuestionMetricsResponse(BaseModel):
    questions: list[QuestionMetric] = Field(default_factory=list)


class ResponseRecord(BaseModel):
    id: str
    answers: list[AnswerItem] = Field(default_factory=list)


class ResponseListResponse(BaseModel):
    responses: list[ResponseRecord] = Field(default_factory=list)
