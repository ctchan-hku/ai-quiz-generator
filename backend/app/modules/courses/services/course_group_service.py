from app.modules.courses.models import CourseGroupListResponse
from app.modules.courses.repositories.course_group_repository import (
    CourseGroupRepository,
)


class CourseGroupService:
    def __init__(self, repository: CourseGroupRepository) -> None:
        self._repository = repository

    async def list_owned_by_user(self, user_id: str) -> CourseGroupListResponse:
        course_groups = await self._repository.find_owned_by_user(user_id)
        return CourseGroupListResponse(course_groups=course_groups)
