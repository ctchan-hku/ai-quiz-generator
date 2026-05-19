from app.modules.data.student_stats.models import TestListResponse, TestRecord
from app.modules.data.student_stats.repositories.question_repository import (
    QuestionRepository,
)
from app.modules.data.student_stats.repositories.test_repository import TestRepository


class ListTestsHandler:
    def __init__(
        self,
        test_repository: TestRepository,
        question_repository: QuestionRepository,
    ) -> None:
        self._test_repository = test_repository
        self._question_repository = question_repository

    async def list_by_course_group_id(self, course_group_id: str) -> TestListResponse:
        tests = await self._test_repository.find_by_course_group_id(course_group_id)
        enriched_tests = [await self._with_questions(test) for test in tests]
        return TestListResponse(tests=enriched_tests)

    async def _with_questions(self, test: TestRecord) -> TestRecord:
        questions = await self._question_repository.find_by_ids_in_order(test.questions)
        return test.model_copy(update={"questions": questions})
