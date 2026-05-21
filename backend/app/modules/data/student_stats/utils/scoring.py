from app.modules.data.student_stats.models import ResponseRecord


def question_score_for_response(
    response: ResponseRecord,
    question_id: str,
) -> int | float:
    for answer in response.answers:
        if answer.question_id == question_id:
            return answer.content.value
    return 0


def total_score_for_response(
    response: ResponseRecord,
    question_ids: set[str],
) -> int | float:
    total = 0
    for answer in response.answers:
        if answer.question_id in question_ids:
            total += answer.content.value
    return total


def student_chose_option_label(
    response: ResponseRecord,
    question_id: str,
    label: str,
) -> bool:
    for answer in response.answers:
        if (
            answer.question_id == question_id
            and answer.content
            and answer.content.label == label
        ):
            return True
    return False
