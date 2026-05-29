from app.domains.questions.models import QuestionRecord
from app.domains.responses.models import ResponseRecord
from app.modules.item_analysis.models import (
    ItemAnalysisReport,
    ItemMetric,
    OptionMetric,
)
from app.modules.item_analysis.utils.confidence_interval import (
    confidence_interval_for_correlation,
    confidence_interval_for_mean,
    metric_index_bounds,
)
from app.modules.item_analysis.utils.correlation import (
    corrected_point_biserial_correlation,
)
from app.modules.item_analysis.utils.distractor_effectiveness import (
    distractor_effectiveness,
)
from app.modules.item_analysis.utils.response_record import (
    is_label_selected,
    question_score_for_response,
    total_score_for_response,
)
from app.modules.item_analysis.utils.score_quartiles import quartile_group_indices


class ItemAnalysisService:
    def build_item_analysis(
        self,
        responses: list[ResponseRecord],
        questions: list[QuestionRecord],
    ) -> ItemAnalysisReport:
        options_by_question = _build_options_by_question(responses, questions)
        difficulty_index_by_question = _build_difficulty_index_by_question(
            responses,
            questions,
        )
        discrimination_index_by_question = _build_discrimination_index_by_question(
            responses,
            questions,
        )

        return ItemAnalysisReport(
            questions=[
                ItemMetric(
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
    total_test_scores_per_student = [
        total_score_for_response(response, question_ids) for response in responses
    ]
    quartiles = quartile_group_indices(total_test_scores_per_student)

    options_by_question: dict[str, list[OptionMetric]] = {}
    for question in questions:
        max_score = max(item.value for item in question.response_nrl.specification)
        options: list[OptionMetric] = []

        for item in sorted(
            question.response_nrl.specification,
            key=lambda specification_item: specification_item.label,
        ):
            selection_flags = [
                float(is_label_selected(response, question.id, item.label))
                for response in responses
            ]
            cohort_attraction = [
                sum(selection_flags[i] for i in group) / len(group) if group else 0.0
                for group in quartiles
            ]
            selection_rate = (
                sum(cohort_attraction) / len(cohort_attraction)
                if cohort_attraction
                else 0.0
            )
            effectiveness = None

            if item.value < max_score:
                effectiveness = distractor_effectiveness(
                    selection_rate,
                    selection_flags,
                    total_test_scores_per_student,
                    (quartiles[0], quartiles[3]),
                )

            options.append(
                OptionMetric(
                    label=item.label,
                    selection_rate=selection_rate,
                    cohort_attraction=cohort_attraction,
                    effectiveness=effectiveness,
                ),
            )

        options_by_question[question.id] = options

    return options_by_question


def _build_difficulty_index_by_question(
    responses: list[ResponseRecord],
    questions: list[QuestionRecord],
) -> dict[str, list[float]]:
    indices: dict[str, list[float]] = {}

    for question in questions:
        max_possible_score = max(
            item.value for item in question.response_nrl.specification
        )
        normalized_scores_per_student = [
            question_score_for_response(response, question.id) / max_possible_score
            for response in responses
        ]
        sample_size = len(normalized_scores_per_student)
        point_estimate = (
            sum(normalized_scores_per_student) / sample_size if sample_size else 0.0
        )
        indices[question.id] = metric_index_bounds(
            point_estimate,
            confidence_interval_for_mean(normalized_scores_per_student),
            clamp_lower=0.0,
            clamp_upper=1.0,
        )

    return indices


def _build_discrimination_index_by_question(
    responses: list[ResponseRecord],
    questions: list[QuestionRecord],
) -> dict[str, list[float]]:
    question_ids = {question.id for question in questions}
    total_test_scores_per_student = [
        total_score_for_response(response, question_ids) for response in responses
    ]
    sample_size = len(responses)

    indices: dict[str, list[float]] = {}
    for question in questions:
        question_scores_per_student = [
            question_score_for_response(response, question.id) for response in responses
        ]
        point_estimate = corrected_point_biserial_correlation(
            question_scores_per_student,
            total_test_scores_per_student,
        )
        indices[question.id] = metric_index_bounds(
            point_estimate,
            confidence_interval_for_correlation(point_estimate, sample_size),
            clamp_lower=-1.0,
            clamp_upper=1.0,
        )
    return indices
