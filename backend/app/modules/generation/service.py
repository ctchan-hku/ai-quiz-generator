import logging

from app.core.actions.derive_question_metrics import DeriveQuestionMetricsAction
from app.modules.generation.helpers.reference_selection import (
    ReferenceQuestion,
    build_reference_questions,
)
from app.modules.item_analysis.service import ItemAnalysisService

logger = logging.getLogger(__name__)


async def load_reference_questions(
    selected_test_ids: list[str],
    derive_metrics_action: DeriveQuestionMetricsAction | None,
) -> list[ReferenceQuestion]:
    if not selected_test_ids:
        return []
    if derive_metrics_action is None:
        logger.warning(
            "selected_test_ids provided but MongoDB is disabled; "
            "skipping reference-question loading",
        )
        return []

    item_analysis_service = ItemAnalysisService()
    reference_questions: list[ReferenceQuestion] = []
    for test_id in selected_test_ids:
        context = await derive_metrics_action.load_by_test_id(test_id)
        if context is None:
            continue
        metrics = item_analysis_service.build_item_analysis(
            context.responses,
            context.questions,
        )
        difficulty_by_question = {
            metric.question_id: metric.difficulty_index for metric in metrics.questions
        }
        reference_questions.extend(
            build_reference_questions(
                context.questions,
                context.responses,
                difficulty_by_question,
            ),
        )
    return reference_questions
