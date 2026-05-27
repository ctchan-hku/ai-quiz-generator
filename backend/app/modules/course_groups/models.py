from pydantic import BaseModel, Field

from app.modules.tests.models import TestSummary


class CourseGroupSummary(BaseModel):
    id: str
    name: str


class CourseGroupWithTests(BaseModel):
    id: str
    name: str
    tests: list[TestSummary] = Field(default_factory=list)


class CourseGroupListResponse(BaseModel):
    course_groups: list[CourseGroupSummary] = Field(default_factory=list)
