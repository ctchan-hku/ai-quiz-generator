import asyncio
from unittest.mock import AsyncMock

import bcrypt
import pytest
from bson import ObjectId
from fastapi import HTTPException

from app.modules.data.auth.models import LoginRequest
from app.modules.data.auth.services.login_service import LoginService
from app.modules.data.student_stats.models import CourseGroupListResponse, CourseGroupSummary


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
def login_service(
    user_repository: AsyncMock,
    course_group_service: AsyncMock,
) -> LoginService:
    return LoginService(user_repository, course_group_service)


def test_login_returns_user_and_course_groups(
    login_service: LoginService,
    user_repository: AsyncMock,
    course_group_service: AsyncMock,
) -> None:
    response = asyncio.run(
        login_service.login(LoginRequest(username="alice", password="secret123")),
    )

    assert response.user_id == "507f1f77bcf86cd799439011"
    assert response.username == "alice"
    assert response.course_groups == [
        CourseGroupSummary(id="cg-1", name="Algebra"),
        CourseGroupSummary(id="cg-2", name="Geometry"),
    ]
    user_repository.find_by_username.assert_awaited_once_with("alice")
    course_group_service.list_by_user_id.assert_awaited_once_with(
        "507f1f77bcf86cd799439011",
    )


def test_login_rejects_unknown_username(
    login_service: LoginService,
    user_repository: AsyncMock,
    course_group_service: AsyncMock,
) -> None:
    user_repository.find_by_username = AsyncMock(return_value=None)

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(
            login_service.login(LoginRequest(username="missing", password="secret123")),
        )

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid credentials"
    course_group_service.list_by_user_id.assert_not_called()


def test_login_rejects_invalid_password(
    login_service: LoginService,
    course_group_service: AsyncMock,
) -> None:
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(
            login_service.login(LoginRequest(username="alice", password="wrong")),
        )

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid credentials"
    course_group_service.list_by_user_id.assert_not_called()
