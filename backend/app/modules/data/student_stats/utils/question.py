from collections import defaultdict

from app.modules.data.student_stats.models import (
    AnswerDistributionResponse,
    LabelCount,
    QuestionAnswerDistribution,
    ResponseRecord,
)


def build_answer_distribution(
    responses: list[ResponseRecord],
) -> AnswerDistributionResponse:
    counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))

    for response in responses:
        for answer in response.answers:
            if not answer.question_id or not answer.content or not answer.content.label:
                continue
            counts[answer.question_id][answer.content.label] += 1

    questions = [
        QuestionAnswerDistribution(
            question_id=question_id,
            label_counts=[
                LabelCount(label=label, count=count)
                for label, count in sorted(label_map.items())
            ],
        )
        for question_id, label_map in sorted(counts.items())
    ]
    return AnswerDistributionResponse(questions=questions)
