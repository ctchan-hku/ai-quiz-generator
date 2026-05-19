from typing import Annotated

from fastapi import APIRouter, Depends

from app.modules.data.student_stats.models import (
    CourseGroupListResponse,
    ResponseListResponse,
    TestListResponse,
)
from app.modules.data.student_stats.services.course_group_service import (
    CourseGroupService,
)
from app.modules.data.student_stats.services.response_service import ResponseService
from app.modules.data.student_stats.services.test_service import TestService
from app.server.dependencies.student_stats import (
    get_course_group_service,
    get_response_service,
    get_test_service,
)

router = APIRouter(prefix="/api")


@router.get("/users/{user_id}/course-groups", response_model=CourseGroupListResponse)
async def list_user_course_groups(
    user_id: str,
    service: Annotated[CourseGroupService, Depends(get_course_group_service)],
) -> CourseGroupListResponse:
    """Return id and name of course groups owned by the given user."""
    return await service.list_owned_by_user(user_id)


@router.get(
    "/course-groups/{course_group_id}/tests",
    response_model=TestListResponse,
)
async def list_course_group_tests(
    course_group_id: str,
    service: Annotated[TestService, Depends(get_test_service)],
) -> TestListResponse:
    """Return tests linked to the course group via course_group_details.id."""
    return await service.list_by_course_group_id(course_group_id)


@router.get("/tests/{test_id}/responses", response_model=ResponseListResponse)
async def list_test_responses(
    test_id: str,
    service: Annotated[ResponseService, Depends(get_response_service)],
) -> ResponseListResponse:
    """Return responses for a test where template.id matches and template.type is test."""
    return await service.list_by_test_id(test_id)
