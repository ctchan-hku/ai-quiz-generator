import asyncio

from pydantic import BaseModel, ConfigDict, Field

from app.core.domain import TestRecord
from app.modules.auth.models import LoginCredentials
from app.modules.auth.service import CredentialAuthService
from app.modules.data.course_groups.service import CourseGroupService
from app.modules.data.questions.repository import QuestionRepository
from app.modules.data.tests.repository import TestRepository


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


class InitializeWorkspaceAction:
    def __init__(
        self,
        auth_service: CredentialAuthService,
        course_group_service: CourseGroupService,
        test_repository: TestRepository,
        question_repository: QuestionRepository,
    ) -> None:
        self._auth_service = auth_service
        self._course_group_service = course_group_service
        self._test_repository = test_repository
        self._question_repository = question_repository

    async def execute(self, credentials: LoginCredentials) -> WorkspaceContext:
        user = await self._auth_service.authenticate(credentials)
        course_groups = await self._course_group_service.list_by_user_id(user.user_id)
        course_groups_with_tests = await asyncio.gather(
            *[
                self._course_group_with_tests(
                    course_group.id,
                    course_group.name,
                )
                for course_group in course_groups
            ],
        )
        return WorkspaceContext(
            user_id=user.user_id,
            username=user.username,
            course_groups=list(course_groups_with_tests),
        )

    async def _course_group_with_tests(
        self,
        course_group_id: str,
        course_group_name: str,
    ) -> CourseGroupWithTests:
        tests = await self._test_repository.find_by_course_group_id(course_group_id)
        enriched_tests = [await self._with_questions(test) for test in tests]
        return CourseGroupWithTests(
            id=course_group_id,
            name=course_group_name,
            tests=[
                TestSummary(
                    id=test.id,
                    name=test.name,
                    num_questions=len(test.questions),
                )
                for test in enriched_tests
            ],
        )

    async def _with_questions(self, test: TestRecord) -> TestRecord:
        questions = await self._question_repository.find_by_ids_in_order(
            test.questions,
        )
        return test.model_copy(update={"questions": questions})
