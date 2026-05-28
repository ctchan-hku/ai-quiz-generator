from pydantic import BaseModel, ConfigDict, Field


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResult(BaseModel):
    user_id: str
    username: str


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
