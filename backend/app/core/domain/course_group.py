from pydantic import BaseModel, Field

from app.core.domain.base import TestSummary


class CourseGroupSummary(BaseModel):
    id: str
    name: str


class CourseGroupWithTests(BaseModel):
    id: str
    name: str
    tests: list[TestSummary] = Field(default_factory=list)
