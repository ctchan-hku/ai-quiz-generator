from dataclasses import dataclass

from app.modules.data.student_stats.constants import DISTRIBUTABLE_QUESTION_TYPES
from app.modules.data.student_stats.models import (
    QuestionMetric,
    QuestionMetricsResponse,
    QuestionRecord,
    ResponseRecord,
)
from app.modules.data.student_stats.repositories.question_repository import (
    QuestionRepository,
)
from app.modules.data.student_stats.repositories.response_repository import (
    ResponseRepository,
)
from app.modules.data.student_stats.repositories.test_repository import TestRepository
from app.modules.data.student_stats.utils.question_metrics import (
    build_difficulty_index_by_question,
    build_discrimination_index_by_question,
    build_label_counts_by_question,
)


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
    ) -> None:
        self._test_repository = test_repository
        self._question_repository = question_repository
        self._response_repository = response_repository

    async def get_by_test_id(self, test_id: str) -> QuestionMetricsResponse:
        context = await self._load_by_test_id(test_id)
        if context is None:
            return QuestionMetricsResponse()

        label_counts_by_question = build_label_counts_by_question(
            context.responses,
            context.questions,
        )
        difficulty_index_by_question = build_difficulty_index_by_question(
            context.responses,
            context.questions,
        )
        discrimination_index_by_question = build_discrimination_index_by_question(
            context.responses,
            context.questions,
        )

        return QuestionMetricsResponse(
            questions=[
                QuestionMetric(
                    question_id=question.id,
                    label_counts=label_counts_by_question.get(question.id, []),
                    difficulty_index=difficulty_index_by_question[question.id],
                    discrimination_index=discrimination_index_by_question[question.id],
                )
                for question in context.questions
            ],
        )

    async def _load_by_test_id(self, test_id: str) -> QuestionMetricsContext | None:
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
