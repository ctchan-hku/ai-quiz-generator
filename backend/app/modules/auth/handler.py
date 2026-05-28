import asyncio

import bcrypt
from fastapi import HTTPException

from app.modules.auth.repository import UserRepository
from app.core.domain.test import TestRecord
from app.modules.auth.models import CourseGroupWithTests, LoginRequest, LoginResponse, TestSummary
from app.modules.data.course_groups.service import CourseGroupService
from app.modules.data.questions.repository import QuestionRepository
from app.modules.data.tests.repository import TestRepository

INVALID_CREDENTIALS = "Invalid credentials"


class LoginHandler:
    def __init__(
        self,
        user_repository: UserRepository,
        course_group_service: CourseGroupService,
        test_repository: TestRepository,
        question_repository: QuestionRepository,
    ) -> None:
        self._user_repository = user_repository
        self._course_group_service = course_group_service
        self._test_repository = test_repository
        self._question_repository = question_repository

    async def login(self, request: LoginRequest) -> LoginResponse:
        user = await self._user_repository.find_by_username(request.username)
        if user is None or not self._password_matches(
            request.password, user["password"]
        ):
            raise HTTPException(status_code=401, detail=INVALID_CREDENTIALS)

        user_id = str(user["_id"])
        course_groups = await self._course_group_service.list_by_user_id(user_id)
        course_groups_with_tests = await asyncio.gather(
            *[
                self._course_group_with_tests(course_group.id, course_group.name)
                for course_group in course_groups
            ],
        )
        return LoginResponse(
            user_id=user_id,
            username=user["username"],
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
        questions = await self._question_repository.find_by_ids_in_order(test.questions)
        return test.model_copy(update={"questions": questions})

    @staticmethod
    def _password_matches(plain_password: str, stored_password: str) -> bool:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            stored_password.encode("utf-8"),
        )
