import logging

from app.modules.generation.helpers.reference_selection import (
    ReferenceQuestion,
    build_reference_questions,
)
from app.core.workflows.student_stats_workflow import StudentStatsWorkflow
from app.modules.student_stats.service import QuestionMetricsService

logger = logging.getLogger(__name__)


async def load_reference_questions(
    selected_test_ids: list[str],
    student_stats_workflow: StudentStatsWorkflow | None,
) -> list[ReferenceQuestion]:
    if not selected_test_ids:
        return []
    if student_stats_workflow is None:
        logger.warning(
            "selected_test_ids provided but MongoDB is disabled; "
            "skipping reference-question loading",
        )
        return []

    metrics_service = QuestionMetricsService()
    reference_questions: list[ReferenceQuestion] = []
    for test_id in selected_test_ids:
        context = await student_stats_workflow.load_by_test_id(test_id)
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
