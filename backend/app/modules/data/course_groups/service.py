from app.modules.data.course_groups.constants import EXCLUDED_NAME_TERMS
from app.modules.data.course_groups.models import CourseGroupRecord
from app.modules.data.course_groups.name_filters import name_contains_excluded_term
from app.modules.data.course_groups.repository import CourseGroupRepository


class CourseGroupService:
    def __init__(self, repository: CourseGroupRepository) -> None:
        self._repository = repository

    async def list_by_user_id(self, user_id: str) -> list[CourseGroupRecord]:
        course_groups = await self._repository.find_by_user_id(user_id)
        return [
            course_group
            for course_group in course_groups
            if not name_contains_excluded_term(
                course_group.name,
                EXCLUDED_NAME_TERMS,
            )
        ]
