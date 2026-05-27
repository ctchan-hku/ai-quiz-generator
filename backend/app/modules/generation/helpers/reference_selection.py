from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from app.modules.questions.models import QuestionRecord
from app.modules.responses.models import ResponseRecord


class ReferenceQuestion(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question_id: str
    prompt: str
    option_labels: list[str] = Field(default_factory=list)
    difficulty_index: tuple[float, float]


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


def build_reference_questions(
    questions: list[QuestionRecord],
    responses: list[ResponseRecord],
    difficulty_by_question: dict[str, list[float]],
) -> list[ReferenceQuestion]:
    reference_questions: list[ReferenceQuestion] = []

    for question in questions:
        prompt = (question.prompt or "").strip()
        if not prompt:
            continue

        bounds = difficulty_by_question.get(question.id)
        if bounds is None or len(bounds) != 2:
            continue

        option_labels = [
            item.label
            for item in sorted(
                question.response_nrl.specification,
                key=lambda specification_item: specification_item.label,
            )
        ]
        reference_questions.append(
            ReferenceQuestion(
                question_id=question.id,
                prompt=prompt,
                option_labels=option_labels,
                difficulty_index=(bounds[0], bounds[1]),
            ),
        )

    return reference_questions


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
            (
                f"Reference question {index} "
                f"(difficulty {lower:.2f}–{upper:.2f}):"
            ),
            f"Stem: {question.prompt}",
            "Options:",
        ]
        for option_label in question.option_labels:
            block.append(f"- {option_label}")
        lines.append("\n".join(block))

    return "\n\n".join(lines)
