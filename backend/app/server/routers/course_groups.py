from typing import Annotated

from fastapi import APIRouter, Depends

from app.modules.data.course_groups.models import CourseGroupSummary
from app.modules.data.course_groups.service import CourseGroupService
from app.server.dependencies.student_stats import get_course_group_service

router = APIRouter(prefix="/api")


@router.get(
    "/users/{user_id}/course-groups",
    response_model=list[CourseGroupSummary],
)
async def list_user_course_groups(
    user_id: str,
    service: Annotated[CourseGroupService, Depends(get_course_group_service)],
) -> list[CourseGroupSummary]:
    """Return id and name of course groups owned by the given user."""
    return await service.list_by_user_id(user_id)
