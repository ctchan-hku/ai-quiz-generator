from collections import defaultdict

from app.modules.data.student_stats.models import (
    OptionMetric,
    QuestionRecord,
    ResponseRecord,
)
from app.modules.data.student_stats.utils.correlation import corrected_point_biserial
from app.modules.data.student_stats.utils.distractor_effectiveness import (
    distractor_discrimination_index,
    distractor_effectiveness_score,
    point_biserial_for_distractor,
)
from app.modules.data.student_stats.utils.scoring import (
    question_score_for_response,
    student_chose_option_label,
    total_score_for_response,
)


def build_options_by_question(
    responses: list[ResponseRecord],
    questions: list[QuestionRecord],
) -> dict[str, list[OptionMetric]]:
    question_ids = {question.id for question in questions}
    counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))

    for response in responses:
        for answer in response.answers:
            if (
                not answer.question_id
                or answer.question_id not in question_ids
                or not answer.content
                or not answer.content.label
            ):
                continue
            counts[answer.question_id][answer.content.label] += 1

    num_students = len(responses)
    total_test_scores = [
        total_score_for_response(response, question_ids) for response in responses
    ]

    options_by_question: dict[str, list[OptionMetric]] = {}
    for question in questions:
        label_counts = counts.get(question.id, {})
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
                chose_option = [
                    float(student_chose_option_label(response, question.id, item.label))
                    for response in responses
                ]
                discrimination_index = distractor_discrimination_index(
                    chose_option,
                    total_test_scores,
                )
                point_biserial = point_biserial_for_distractor(
                    chose_option,
                    total_test_scores,
                )
                effectiveness = distractor_effectiveness_score(
                    selection_rate,
                    discrimination_index,
                    point_biserial,
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


def build_difficulty_index_by_question(
    responses: list[ResponseRecord],
    questions: list[QuestionRecord],
) -> dict[str, float]:
    indices: dict[str, float] = {}

    for question in questions:
        max_possible_score = max(
            item.value for item in question.response_nrl.specification
        )
        item_scores = [
            question_score_for_response(response, question.id) for response in responses
        ]
        n = len(item_scores)
        indices[question.id] = sum(item_scores) / (n * max_possible_score) if n else 0.0

    return indices


def build_discrimination_index_by_question(
    responses: list[ResponseRecord],
    questions: list[QuestionRecord],
) -> dict[str, float]:
    question_ids = {question.id for question in questions}
    total_test_scores = [
        total_score_for_response(response, question_ids) for response in responses
    ]

    return {
        question.id: corrected_point_biserial(
            [
                question_score_for_response(response, question.id)
                for response in responses
            ],
            total_test_scores,
        )
        for question in questions
    }
