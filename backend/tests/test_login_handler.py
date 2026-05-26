import asyncio
from unittest.mock import AsyncMock

import bcrypt
import pytest
from bson import ObjectId
from fastapi import HTTPException

from app.modules.data.auth.handlers.login_handler import LoginHandler
from app.modules.data.auth.models import LoginRequest
from app.modules.data.student_stats.models import (
    CourseGroupListResponse,
    CourseGroupSummary,
    CourseGroupWithTests,
    TestRecord,
    TestSummary,
)


@pytest.fixture
def password_hash() -> str:
    return bcrypt.hashpw(b"secret123", bcrypt.gensalt()).decode("utf-8")


@pytest.fixture
def user_document(password_hash: str) -> dict:
    return {
        "_id": ObjectId("507f1f77bcf86cd799439011"),
        "username": "alice",
        "password": password_hash,
    }


@pytest.fixture
def user_repository(user_document: dict) -> AsyncMock:
    repository = AsyncMock()
    repository.find_by_username = AsyncMock(return_value=user_document)
    return repository


@pytest.fixture
def course_group_service() -> AsyncMock:
    service = AsyncMock()
    service.list_by_user_id = AsyncMock(
        return_value=CourseGroupListResponse(
            course_groups=[
                CourseGroupSummary(id="cg-1", name="Algebra"),
                CourseGroupSummary(id="cg-2", name="Geometry"),
            ],
        ),
    )
    return service


@pytest.fixture
def test_repository() -> AsyncMock:
    repository = AsyncMock()

    async def find_by_course_group_id(course_group_id: str) -> list[TestRecord]:
        if course_group_id == "cg-1":
            return [
                TestRecord(id="test-1", name="Quiz A", questions=["q-1", "q-2"]),
                TestRecord(id="test-2", name="Quiz B", questions=["q-3"]),
            ]
        return [TestRecord(id="test-3", name="Final", questions=["q-4", "q-5", "q-6"])]

    repository.find_by_course_group_id = AsyncMock(side_effect=find_by_course_group_id)
    return repository


@pytest.fixture
def question_repository() -> AsyncMock:
    repository = AsyncMock()
    repository.find_by_ids_in_order = AsyncMock(
        side_effect=lambda question_ids: [{"id": question_id} for question_id in question_ids],
    )
    return repository


@pytest.fixture
def login_handler(
    user_repository: AsyncMock,
    course_group_service: AsyncMock,
    test_repository: AsyncMock,
    question_repository: AsyncMock,
) -> LoginHandler:
    return LoginHandler(
        user_repository,
        course_group_service,
        test_repository,
        question_repository,
    )


def test_login_returns_user_course_groups_and_tests(
    login_handler: LoginHandler,
    user_repository: AsyncMock,
    course_group_service: AsyncMock,
    test_repository: AsyncMock,
    question_repository: AsyncMock,
) -> None:
    response = asyncio.run(
        login_handler.login(LoginRequest(username="alice", password="secret123")),
    )

    assert response.user_id == "507f1f77bcf86cd799439011"
    assert response.username == "alice"
    assert response.course_groups == [
        CourseGroupWithTests(
            id="cg-1",
            name="Algebra",
            tests=[
                TestSummary(id="test-1", name="Quiz A", num_questions=2),
                TestSummary(id="test-2", name="Quiz B", num_questions=1),
            ],
        ),
        CourseGroupWithTests(
            id="cg-2",
            name="Geometry",
            tests=[TestSummary(id="test-3", name="Final", num_questions=3)],
        ),
    ]
    user_repository.find_by_username.assert_awaited_once_with("alice")
    course_group_service.list_by_user_id.assert_awaited_once_with(
        "507f1f77bcf86cd799439011",
    )
    assert test_repository.find_by_course_group_id.await_count == 2
    assert question_repository.find_by_ids_in_order.await_count == 3


def test_login_rejects_unknown_username(
    login_handler: LoginHandler,
    user_repository: AsyncMock,
    course_group_service: AsyncMock,
    test_repository: AsyncMock,
) -> None:
    user_repository.find_by_username = AsyncMock(return_value=None)

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(
            login_handler.login(LoginRequest(username="missing", password="secret123")),
        )

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid credentials"
    course_group_service.list_by_user_id.assert_not_called()
    test_repository.find_by_course_group_id.assert_not_called()


def test_login_rejects_invalid_password(
    login_handler: LoginHandler,
    course_group_service: AsyncMock,
    test_repository: AsyncMock,
) -> None:
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(
            login_handler.login(LoginRequest(username="alice", password="wrong")),
        )

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid credentials"
    course_group_service.list_by_user_id.assert_not_called()
    test_repository.find_by_course_group_id.assert_not_called()
