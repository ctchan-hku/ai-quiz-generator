from dataclasses import dataclass

from app.modules.data.student_stats.constants.question_metrics import (
    DISTRIBUTABLE_QUESTION_TYPES,
)
from app.modules.data.student_stats.models import (
    QuestionMetricsResponse,
)
from app.modules.data.student_stats.services.question_metrics_service import (
    QuestionMetricsService,
)
from app.modules.questions.models import QuestionRecord
from app.modules.questions.repository import QuestionRepository
from app.modules.responses.models import ResponseRecord
from app.modules.responses.repository import ResponseRepository
from app.modules.tests.repository import TestRepository


@dataclass
class QuestionMetricsContext:
    questions: list[QuestionRecord]
    responses: list[ResponseRecord]


class QuestionMetricsHandler:
    def __init__(
        self,
        test_repository: TestRepository,
        question_repository: QuestionRepository,
        response_repository: ResponseRepository,
        question_metrics_service: QuestionMetricsService,
    ) -> None:
        self._test_repository = test_repository
        self._question_repository = question_repository
        self._response_repository = response_repository
        self._question_metrics_service = question_metrics_service

    async def get_by_test_id(self, test_id: str) -> QuestionMetricsResponse:
        context = await self.load_by_test_id(test_id)
        if context is None:
            return QuestionMetricsResponse()

        return self._question_metrics_service.build_question_metrics(
            context.responses,
            context.questions,
        )

    async def load_by_test_id(self, test_id: str) -> QuestionMetricsContext | None:
        test = await self._test_repository.find_by_id(test_id)
        if test is None:
            return None

        questions = await self._question_repository.find_by_ids_in_order(
            test.questions,
            types=DISTRIBUTABLE_QUESTION_TYPES,
        )
        return QuestionMetricsContext(
            questions=[
                question
                for question in questions
                if any(item.value != 0 for item in question.response_nrl.specification)
            ],
            responses=await self._response_repository.find_by_test_id(test_id),
        )
