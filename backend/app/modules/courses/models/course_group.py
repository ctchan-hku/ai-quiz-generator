from pydantic import BaseModel, Field


class CourseGroupSummary(BaseModel):
    id: str
    name: str


class CourseGroupListResponse(BaseModel):
    course_groups: list[CourseGroupSummary] = Field(default_factory=list)
