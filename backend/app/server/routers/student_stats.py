from typing import Annotated

from fastapi import APIRouter, Depends

from app.modules.data.student_stats.handlers.list_tests_handler import ListTestsHandler
from app.modules.data.student_stats.handlers.question_metrics_handler import (
    QuestionMetricsHandler,
)
from app.modules.data.student_stats.models import (
    CourseGroupListResponse,
    QuestionMetricsResponse,
    ResponseListResponse,
    TestListResponse,
)
from app.modules.data.student_stats.services.course_group_service import (
    CourseGroupService,
)
from app.modules.data.student_stats.services.response_service import ResponseService
from app.server.dependencies.student_stats import (
    get_course_group_service,
    get_list_tests_handler,
    get_question_metrics_handler,
    get_response_service,
)

router = APIRouter(prefix="/api")


@router.get("/users/{user_id}/course-groups", response_model=CourseGroupListResponse)
async def list_user_course_groups(
    user_id: str,
    service: Annotated[CourseGroupService, Depends(get_course_group_service)],
) -> CourseGroupListResponse:
    """Return id and name of course groups owned by the given user."""
    return await service.list_by_user_id(user_id)


@router.get(
    "/course-groups/{course_group_id}/tests",
    response_model=TestListResponse,
)
async def list_course_group_tests(
    course_group_id: str,
    handler: Annotated[ListTestsHandler, Depends(get_list_tests_handler)],
) -> TestListResponse:
    """Return tests linked to the course group via course_group_details.id."""
    return await handler.list_by_course_group_id(course_group_id)


@router.get("/tests/{test_id}/responses", response_model=ResponseListResponse)
async def list_test_responses(
    test_id: str,
    service: Annotated[ResponseService, Depends(get_response_service)],
) -> ResponseListResponse:
    """Return responses for a test where template.id matches and template.type is test."""
    return await service.list_by_test_id(test_id)


@router.get(
    "/tests/{test_id}/question-metrics",
    response_model=QuestionMetricsResponse,
)
async def get_test_question_metrics(
    test_id: str,
    handler: Annotated[QuestionMetricsHandler, Depends(get_question_metrics_handler)],
) -> QuestionMetricsResponse:
    """Return option selection rates, difficulty index, and discrimination index per scored question."""
    return await handler.get_by_test_id(test_id)
