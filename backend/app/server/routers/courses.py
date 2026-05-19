from typing import Annotated

from fastapi import APIRouter, Depends

from app.modules.courses.models import CourseGroupListResponse
from app.modules.courses.services.course_group_service import CourseGroupService
from app.server.dependencies.courses import get_course_group_service

router = APIRouter(prefix="/api")


@router.get("/users/{user_id}/course-groups", response_model=CourseGroupListResponse)
async def list_user_course_groups(
    user_id: str,
    service: Annotated[CourseGroupService, Depends(get_course_group_service)],
) -> CourseGroupListResponse:
    """Return id and name of course groups owned by the given user."""
    return await service.list_owned_by_user(user_id)
