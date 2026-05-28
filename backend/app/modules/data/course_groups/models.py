from pydantic import BaseModel


class CourseGroupSummary(BaseModel):
    id: str
    name: str
