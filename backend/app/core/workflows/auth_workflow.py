import asyncio

from pydantic import BaseModel, Field

from app.core.domain.test import TestRecord
from app.modules.auth.handler import LoginHandler
from app.modules.auth.models import (
    CourseGroupWithTests,
    LoginRequest,
    LoginResult,
    TestSummary,
)
from app.modules.data.course_groups.service import CourseGroupService
from app.modules.data.questions.repository import QuestionRepository
from app.modules.data.tests.repository import TestRepository


class LoginResponse(BaseModel):
    user_id: str
    username: str
    course_groups: list[CourseGroupWithTests] = Field(default_factory=list)


class AuthWorkflow:
    def __init__(
        self,
        login_handler: LoginHandler,
        course_group_service: CourseGroupService,
        test_repository: TestRepository,
        question_repository: QuestionRepository,
    ) -> None:
        self._login_handler = login_handler
        self._course_group_service = course_group_service
        self._test_repository = test_repository
        self._question_repository = question_repository

    async def login_and_enrich(self, request: LoginRequest) -> LoginResponse:
        result = await self._login_handler.login(request)
        course_groups = await self._course_group_service.list_by_user_id(
            result.user_id,
        )
        course_groups_with_tests = await asyncio.gather(
            *[
                self._course_group_with_tests(
                    course_group.id,
                    course_group.name,
                )
                for course_group in course_groups
            ],
        )
        return LoginResponse(
            user_id=result.user_id,
            username=result.username,
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
