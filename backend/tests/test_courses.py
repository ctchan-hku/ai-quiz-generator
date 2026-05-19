from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

from app.main import app
from app.modules.courses.models import CourseGroupListResponse, CourseGroupSummary
from app.modules.courses.services.course_group_service import CourseGroupService
from app.server.dependencies.courses import get_course_group_service


def test_list_user_course_groups_returns_503_without_mongodb_uri() -> None:
    with TestClient(app) as client:
        response = client.get("/api/users/user-123/course-groups")

    assert response.status_code == 503
    assert "Database is disabled" in response.json()["detail"]


def test_list_user_course_groups_returns_owned_groups() -> None:
    mock_service = AsyncMock(spec=CourseGroupService)
    mock_service.list_owned_by_user = AsyncMock(
        return_value=CourseGroupListResponse(
            course_groups=[
                CourseGroupSummary(id="cg-1", name="Algebra"),
                CourseGroupSummary(id="cg-2", name="Biology"),
            ]
        )
    )

    app.dependency_overrides[get_course_group_service] = lambda: mock_service
    try:
        with TestClient(app) as client:
            response = client.get("/api/users/user-123/course-groups")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["course_groups"] == [
        {"id": "cg-1", "name": "Algebra"},
        {"id": "cg-2", "name": "Biology"},
    ]
    mock_service.list_owned_by_user.assert_awaited_once_with("user-123")
