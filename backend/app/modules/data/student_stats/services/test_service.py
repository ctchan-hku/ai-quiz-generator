from app.modules.data.student_stats.models import TestListResponse
from app.modules.data.student_stats.repositories.test_repository import TestRepository


class TestService:
    __test__ = False

    def __init__(self, repository: TestRepository) -> None:
        self._repository = repository

    async def list_by_course_group_id(self, course_group_id: str) -> TestListResponse:
        tests = await self._repository.find_by_course_group_id(course_group_id)
        return TestListResponse(tests=tests)
