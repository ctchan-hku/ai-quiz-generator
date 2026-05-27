from pydantic import BaseModel, Field

from app.modules.course_groups.models import CourseGroupWithTests


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    user_id: str
    username: str
    course_groups: list[CourseGroupWithTests] = Field(default_factory=list)
