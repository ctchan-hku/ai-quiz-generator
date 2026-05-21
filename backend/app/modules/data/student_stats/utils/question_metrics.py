from collections import defaultdict

from app.modules.data.student_stats.models import (
    OptionMetric,
    QuestionRecord,
    ResponseRecord,
)
from app.modules.data.student_stats.utils.correlation import corrected_point_biserial
from app.modules.data.student_stats.utils.scoring import (
    question_score_for_response,
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

    options_by_question: dict[str, list[OptionMetric]] = {}
    for question_id, label_map in counts.items():
        total = sum(label_map.values())
        options_by_question[question_id] = [
            OptionMetric(label=label, selection_rate=count / total)
            for label, count in sorted(label_map.items())
        ]
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
