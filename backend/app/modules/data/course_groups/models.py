from pydantic import BaseModel


class CourseGroupRecord(BaseModel):
    id: str
    name: str
