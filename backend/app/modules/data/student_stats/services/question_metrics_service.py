from app.modules.data.student_stats.models import (
    OptionMetric,
    QuestionMetric,
    QuestionMetricsResponse,
    QuestionRecord,
    ResponseRecord,
)
from app.modules.data.student_stats.utils.correlation import (
    corrected_point_biserial_correlation,
)
from app.modules.data.student_stats.utils.distractor_effectiveness import (
    distractor_effectiveness,
)
from app.modules.data.student_stats.utils.response_record import (
    count_label_selections_by_question,
    is_label_selected,
    question_score_for_response,
    total_score_for_response,
)


class QuestionMetricsService:
    def build_question_metrics(
        self,
        responses: list[ResponseRecord],
        questions: list[QuestionRecord],
    ) -> QuestionMetricsResponse:
        options_by_question = _build_options_by_question(responses, questions)
        difficulty_index_by_question = _build_difficulty_index_by_question(
            responses,
            questions,
        )
        discrimination_index_by_question = _build_discrimination_index_by_question(
            responses,
            questions,
        )

        return QuestionMetricsResponse(
            questions=[
                QuestionMetric(
                    question_id=question.id,
                    options=options_by_question.get(question.id, []),
                    difficulty_index=difficulty_index_by_question[question.id],
                    discrimination_index=discrimination_index_by_question[question.id],
                )
                for question in questions
            ],
        )


def _build_options_by_question(
    responses: list[ResponseRecord],
    questions: list[QuestionRecord],
) -> dict[str, list[OptionMetric]]:
    question_ids = {question.id for question in questions}
    counts_per_label = count_label_selections_by_question(responses, question_ids)
    num_students = len(responses)
    total_test_scores_per_student = [
        total_score_for_response(response, question_ids) for response in responses
    ]

    options_by_question: dict[str, list[OptionMetric]] = {}
    for question in questions:
        label_counts = counts_per_label.get(question.id, {})
        max_score = max(item.value for item in question.response_nrl.specification)
        options: list[OptionMetric] = []

        for item in sorted(
            question.response_nrl.specification,
            key=lambda specification_item: specification_item.label,
        ):
            count = label_counts.get(item.label, 0)
            selection_rate = count / num_students if num_students else 0.0
            effectiveness = None

            if item.value < max_score:
                selection_flags = [
                    float(is_label_selected(response, question.id, item.label))
                    for response in responses
                ]
                effectiveness = distractor_effectiveness(
                    selection_rate,
                    selection_flags,
                    total_test_scores_per_student,
                )

            options.append(
                OptionMetric(
                    label=item.label,
                    selection_rate=selection_rate,
                    effectiveness=effectiveness,
                ),
            )

        options_by_question[question.id] = options

    return options_by_question


def _build_difficulty_index_by_question(
    responses: list[ResponseRecord],
    questions: list[QuestionRecord],
) -> dict[str, float]:
    indices: dict[str, float] = {}

    for question in questions:
        max_possible_score = max(
            item.value for item in question.response_nrl.specification
        )
        question_scores_per_student = [
            question_score_for_response(response, question.id) for response in responses
        ]
        n = len(question_scores_per_student)
        indices[question.id] = (
            sum(question_scores_per_student) / (n * max_possible_score) if n else 0.0
        )

    return indices


def _build_discrimination_index_by_question(
    responses: list[ResponseRecord],
    questions: list[QuestionRecord],
) -> dict[str, float]:
    question_ids = {question.id for question in questions}
    total_test_scores_per_student = [
        total_score_for_response(response, question_ids) for response in responses
    ]

    return {
        question.id: corrected_point_biserial_correlation(
            [
                question_score_for_response(response, question.id)
                for response in responses
            ],
            total_test_scores_per_student,
        )
        for question in questions
    }
