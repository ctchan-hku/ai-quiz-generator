from typing import Any
from pydantic import BaseModel, ConfigDict, Field


# --- Shared & Base Domain Models ---

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


class WorkspaceContext(BaseModel):
    user_id: str
    username: str
    course_groups: list[CourseGroupWithTests] = Field(default_factory=list)


# --- Question Domain Models ---

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


# --- Response Domain Models ---

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


# --- Test Domain Models ---

class TestRecord(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    __test__ = False

    id: str
    name: str
    questions: list[Any] = Field(default_factory=list)
    grade_cutoff: list[Any] = Field(default_factory=list)
