"""Pydantic model for one multiple-choice question (quiz items and generate/question payloads)."""

from typing import Any, ClassVar, Literal

from pydantic import BaseModel, model_validator

from app.modules.generation.config import prompts
from app.modules.generation.config.mc_question import (
    MC_QUESTION_CORRECT_INDICES_MIN_COUNT,
    MC_QUESTION_OPTION_COUNT_MAX,
    MC_QUESTION_OPTION_COUNT_MIN,
)
from app.modules.generation.helpers.options import truncate_options


class MultipleChoiceQuestion(BaseModel):
    """Only supported question shape across generate and export APIs."""

    question_type: Literal["multiple_choice"]
    question: str
    options: list[str]
    correct_indices: list[int]
    explanation: str

    constraints: ClassVar[str] = prompts.MULTIPLE_CHOICE_CONSTRAINTS
    chain_of_thought: ClassVar[str] = prompts.MC_QUESTION_CHAIN_OF_THOUGHT

    @model_validator(mode="before")
    @classmethod
    def truncate_excess_options(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        options = data.get("options")
        ci = data.get("correct_indices")
        if not isinstance(options, list) or not isinstance(ci, list):
            return data
        if len(options) <= MC_QUESTION_OPTION_COUNT_MAX:
            return data
        new_o, new_ci = truncate_options(options, ci)
        return {**data, "options": new_o, "correct_indices": new_ci}

    @model_validator(mode="after")
    def validate_options_and_answers(self):
        n = len(self.options)
        if n < MC_QUESTION_OPTION_COUNT_MIN or n > MC_QUESTION_OPTION_COUNT_MAX:
            raise ValueError(
                "multiple_choice requires between "
                f"{MC_QUESTION_OPTION_COUNT_MIN} and {MC_QUESTION_OPTION_COUNT_MAX} options, got {n}"
            )

        ci = self.correct_indices
        if len(ci) < MC_QUESTION_CORRECT_INDICES_MIN_COUNT:
            raise ValueError(
                "multiple_choice correct_indices must list at least "
                f"{MC_QUESTION_CORRECT_INDICES_MIN_COUNT} correct answer(s), got {len(ci)}"
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
