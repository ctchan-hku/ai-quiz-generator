from pydantic import BaseModel, ConfigDict, Field


class WorkspaceCredentials(BaseModel):
    username: str
    password: str


class AuthenticationResult(BaseModel):
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


class WorkspaceContext(BaseModel):
    user_id: str
    username: str
    course_groups: list[CourseGroupWithTests] = Field(default_factory=list)
