import logging

from app.modules.generation.helpers.reference_selection import (
    ReferenceQuestion,
    build_reference_questions,
)
from app.modules.student_stats.handler import QuestionMetricsHandler
from app.modules.student_stats.service import QuestionMetricsService

logger = logging.getLogger(__name__)


async def load_reference_questions(
    selected_test_ids: list[str],
    question_metrics_handler: QuestionMetricsHandler | None,
) -> list[ReferenceQuestion]:
    if not selected_test_ids:
        return []
    if question_metrics_handler is None:
        logger.warning(
            "selected_test_ids provided but MongoDB is disabled; "
            "skipping reference-question loading",
        )
        return []

    metrics_service = QuestionMetricsService()
    reference_questions: list[ReferenceQuestion] = []
    for test_id in selected_test_ids:
        context = await question_metrics_handler.load_by_test_id(test_id)
        if context is None:
            continue
        metrics = metrics_service.build_question_metrics(
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
