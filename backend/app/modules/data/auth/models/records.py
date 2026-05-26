from pydantic import BaseModel, Field

from app.modules.data.student_stats.models import CourseGroupSummary


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    user_id: str
    username: str
    course_groups: list[CourseGroupSummary] = Field(default_factory=list)
