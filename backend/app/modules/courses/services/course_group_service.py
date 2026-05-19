from app.modules.courses.constants import EXCLUDED_NAME_TERMS
from app.modules.courses.models import CourseGroupListResponse
from app.modules.courses.repositories.course_group_repository import (
    CourseGroupRepository,
)
from app.modules.courses.utils import name_contains_excluded_term


class CourseGroupService:
    def __init__(self, repository: CourseGroupRepository) -> None:
        self._repository = repository

    async def list_owned_by_user(self, user_id: str) -> CourseGroupListResponse:
        course_groups = await self._repository.find_owned_by_user(user_id)
        visible_course_groups = [
            course_group
            for course_group in course_groups
            if not name_contains_excluded_term(
                course_group.name,
                EXCLUDED_NAME_TERMS,
            )
        ]
        return CourseGroupListResponse(course_groups=visible_course_groups)
