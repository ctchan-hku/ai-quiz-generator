from dataclasses import dataclass

from app.domains.questions.models import QuestionRecord
from app.domains.questions.repository import QuestionRepository
from app.domains.responses.models import ResponseRecord
from app.domains.responses.repository import ResponseRepository
from app.domains.tests.repository import TestRepository
from app.features.item_analysis.models import ItemAnalysisReport
from app.features.item_analysis.service import ItemAnalysisService


@dataclass
class ItemAnalysisContext:
    questions: list[QuestionRecord]
    responses: list[ResponseRecord]


@dataclass
class TestQuestionMetrics:
    test_id: str
    context: ItemAnalysisContext
    report: ItemAnalysisReport


class DeriveQuestionMetricsAction:
    def __init__(
        self,
        test_repository: TestRepository,
        question_repository: QuestionRepository,
        response_repository: ResponseRepository,
        item_analysis_service: ItemAnalysisService,
    ) -> None:
        self._test_repository = test_repository
        self._question_repository = question_repository
        self._response_repository = response_repository
        self._item_analysis_service = item_analysis_service

    async def execute(self, test_ids: list[str]) -> list[TestQuestionMetrics]:
        results: list[TestQuestionMetrics] = []
        for test_id in test_ids:
            context = await self._load_by_test_id(test_id)
            if context is None:
                continue
            results.append(
                TestQuestionMetrics(
                    test_id=test_id,
                    context=context,
                    report=self._item_analysis_service.build_item_analysis(
                        context.responses,
                        context.questions,
                    ),
                ),
            )
        return results

    async def _load_by_test_id(self, test_id: str) -> ItemAnalysisContext | None:
        test = await self._test_repository.find_by_id(test_id)
        if test is None:
            return None

        questions = await self._question_repository.find_by_ids_in_order(
            test.questions,
        )
        return ItemAnalysisContext(
            questions=[
                question
                for question in questions
                if any(item.value != 0 for item in question.response_nrl.specification)
            ],
            responses=await self._response_repository.find_by_test_id(test_id),
        )
