from collections import defaultdict

from app.modules.data.student_stats.models import AnswerItem, ResponseRecord


def _has_valid_answer (
    answer: AnswerItem,
    question_ids: set[str],
) -> bool:
    return answer.question_id in question_ids and answer.content is not None


def count_label_selections_by_question(
    responses: list[ResponseRecord],
    question_ids: set[str],
) -> dict[str, dict[str, int]]:
    counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for response in responses:
        for answer in response.answers:
            if _has_valid_answer (answer, question_ids):
                counts[answer.question_id][answer.content.label] += 1
    return counts


def question_score_for_response(
    response: ResponseRecord,
    question_id: str,
) -> int | float:
    for answer in response.answers:
        if _has_valid_answer (answer, {question_id}):
            return answer.content.value
    return 0


def total_score_for_response(
    response: ResponseRecord,
    question_ids: set[str],
) -> int | float:
    total = 0
    for answer in response.answers:
        if _has_valid_answer (answer, question_ids):
            total += answer.content.value
    return total


def is_label_selected(
    response: ResponseRecord,
    question_id: str,
    label: str,
) -> bool:
    for answer in response.answers:
        if _has_valid_answer (answer, {question_id}) and answer.content.label == label:
            return True
    return False
