"""Quiz API models — only ``multiple_choice`` questions are supported."""

from typing import ClassVar, Literal

from pydantic import BaseModel, ConfigDict, model_validator

from app.models.mcq_constraints import (
    MCQ_CORRECT_INDICES_MIN_COUNT,
    MCQ_OPTION_COUNT_MAX,
    MCQ_OPTION_COUNT_MIN,
)
from app.services import prompts


class MultipleChoiceQuestion(BaseModel):
    """Only supported question shape across generate and export APIs."""

    question_type: Literal["multiple_choice"]
    question: str
    options: list[str]
    correct_indices: list[int]
    explanation: str

    instructions: ClassVar[str] = f"{prompts.MULTIPLE_CHOICE_INSTRUCTIONS}\n"

    @model_validator(mode="after")
    def validate_options_and_answers(self):
        n = len(self.options)
        if n < MCQ_OPTION_COUNT_MIN or n > MCQ_OPTION_COUNT_MAX:
            raise ValueError(
                "multiple_choice requires between "
                f"{MCQ_OPTION_COUNT_MIN} and {MCQ_OPTION_COUNT_MAX} options, got {n}"
            )

        ci = self.correct_indices
        if len(ci) < MCQ_CORRECT_INDICES_MIN_COUNT:
            raise ValueError(
                "multiple_choice correct_indices must list at least "
                f"{MCQ_CORRECT_INDICES_MIN_COUNT} correct answer(s), got {len(ci)}"
            )

        seen: set[int] = set()
        for i in ci:
            if i < 0 or i >= n:
                raise ValueError(
                    f"correct_indices value {i} out of range for {n} option(s)"
                )
            if i in seen:
                raise ValueError(f"duplicate index in correct_indices: {i}")
            seen.add(i)

        return self


QuizQuestion = MultipleChoiceQuestion


class Quiz(BaseModel):
    questions: list[MultipleChoiceQuestion]


class QuizResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    questions: list[MultipleChoiceQuestion]
    model_used: str
    source: Literal["topic", "file"]
    truncated: bool = False
