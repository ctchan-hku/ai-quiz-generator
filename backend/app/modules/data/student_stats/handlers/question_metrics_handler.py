from app.modules.data.student_stats.constants import DISTRIBUTABLE_QUESTION_TYPES
from app.modules.data.student_stats.models import AnswerDistributionResponse
from app.modules.data.student_stats.repositories.question_repository import (
    QuestionRepository,
)
from app.modules.data.student_stats.repositories.response_repository import (
    ResponseRepository,
)
from app.modules.data.student_stats.repositories.test_repository import TestRepository
from app.modules.data.student_stats.utils.question import build_answer_distribution


class QuestionMetricsHandler:
    def __init__(
        self,
        test_repository: TestRepository,
        question_repository: QuestionRepository,
        response_repository: ResponseRepository,
    ) -> None:
        self._test_repository = test_repository
        self._question_repository = question_repository
        self._response_repository = response_repository

    async def get_distribution_by_test_id(
        self,
        test_id: str,
    ) -> AnswerDistributionResponse:
        test = await self._test_repository.find_by_id(test_id)
        if test is None:
            return AnswerDistributionResponse()

        questions = await self._question_repository.find_by_ids_in_order(
            test.questions,
            types=DISTRIBUTABLE_QUESTION_TYPES,
        )
        question_ids = {question.id for question in questions}
        responses = await self._response_repository.find_by_test_id(test_id)
        return build_answer_distribution(responses, question_ids)
