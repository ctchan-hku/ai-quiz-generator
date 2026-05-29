from __future__ import annotations

import logging

from pydantic import BaseModel, ConfigDict, Field

from app.core.actions.derive_question_metrics import DeriveQuestionMetricsAction

logger = logging.getLogger(__name__)


class ReferenceQuestion(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question_id: str
    prompt: str
    option_labels: list[str] = Field(default_factory=list)
    difficulty_index: tuple[float, float]


async def reference_questions_for_tests(
    test_ids: list[str],
    action: DeriveQuestionMetricsAction | None,
) -> list[ReferenceQuestion]:
    if not test_ids:
        return []
    if action is None:
        logger.warning(
            "selected_test_ids provided but MongoDB is disabled; "
            "skipping reference-question loading",
        )
        return []

    reference_questions: list[ReferenceQuestion] = []
    for result in await action.execute(test_ids):
        questions_by_id = {
            question.id: question for question in result.context.questions
        }
        for metric in result.report.questions:
            question = questions_by_id.get(metric.question_id)
            if question is None:
                continue

            prompt = (question.prompt or "").strip()
            if not prompt or len(metric.difficulty_index) != 2:
                continue

            reference_questions.append(
                ReferenceQuestion(
                    question_id=question.id,
                    prompt=prompt,
                    option_labels=[
                        item.label
                        for item in sorted(
                            question.response_nrl.specification,
                            key=lambda specification_item: specification_item.label,
                        )
                    ],
                    difficulty_index=(
                        metric.difficulty_index[0],
                        metric.difficulty_index[1],
                    ),
                ),
            )

    return reference_questions


def distance_to_difficulty_interval(
    target: float,
    lower: float,
    upper: float,
) -> float:
    if lower <= target <= upper:
        return 0.0
    if target < lower:
        return lower - target
    return target - upper


def select_closest_questions(
    candidates: list[ReferenceQuestion],
    target_difficulty: float,
    *,
    limit: int = 5,
) -> list[ReferenceQuestion]:
    if not candidates:
        return []

    ranked = sorted(
        candidates,
        key=lambda question: (
            distance_to_difficulty_interval(
                target_difficulty,
                question.difficulty_index[0],
                question.difficulty_index[1],
            ),
            question.question_id,
        ),
    )
    return ranked[:limit]


def format_difficulty_reference_context(
    target_difficulty: float,
    selected: list[ReferenceQuestion],
) -> str:
    lines = [
        (
            "Difficulty reference only. Use the target index and reference questions "
            "below to calibrate how challenging new stems should be — not for style, "
            "wording, or option format."
        ),
        f"Target difficulty index: {target_difficulty:.2f}",
    ]

    if not selected:
        lines.append(
            "No reference questions were available from the selected course tests.",
        )
        return "\n\n".join(lines)

    for index, question in enumerate(selected, start=1):
        lower, upper = question.difficulty_index
        block = [
            (f"Reference question {index} (difficulty {lower:.2f}–{upper:.2f}):"),
            f"Stem: {question.prompt}",
            "Options:",
        ]
        for option_label in question.option_labels:
            block.append(f"- {option_label}")
        lines.append("\n".join(block))

    return "\n\n".join(lines)
