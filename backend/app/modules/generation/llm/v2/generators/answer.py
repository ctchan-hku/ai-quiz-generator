"""LLM step: derive exact answers and explanations for stems from question stems."""

from typing import Any, ClassVar

from pydantic import BaseModel, ConfigDict

from app.modules.generation.config.prompts import JSON_OUTPUT_REMINDER
from app.modules.generation.llm.core.llm_json_generator import LlmJsonGenerator
from app.modules.generation.llm.v2.config.completion_tokens import (
    ANSWER_STEP_TOKEN_BUDGET,
    completion_max_tokens_for_items,
)
from app.modules.generation.llm.v2.config.prompt import (
    ANSWER_GENERATOR_CHAIN_OF_THOUGHT,
    ANSWER_GENERATOR_ROLE_DEFAULT,
)
from app.modules.generation.services.prompter import CHAT_COMPLETION_KWARGS


class GeneratedAnswersPayload(BaseModel):
    """Top-level JSON from the answer generator: one row per input stem."""

    model_config = ConfigDict(extra="forbid")

    class Row(BaseModel):
        """One solved stem: exact answer plus derivation only in ``explanation``."""

        model_config = ConfigDict(extra="forbid")

        answer: str
        explanation: str

    answers: list[Row]


class AnswerGenerator(LlmJsonGenerator[GeneratedAnswersPayload]):
    """For each question stem, produce an exact `answer` and a separate `explanation` (reasoning only)."""

    parse_response_model: ClassVar[type[GeneratedAnswersPayload]] = (
        GeneratedAnswersPayload
    )

    def __init__(
        self,
        *,
        questions: list[str],
        requirements: str = "",
    ) -> None:
        if not questions:
            raise ValueError("questions must be non-empty")
        self._questions = questions
        self._requirements = requirements

    @property
    def role_definition(self) -> str:
        return ANSWER_GENERATOR_ROLE_DEFAULT

    @property
    def _chat_completion(self) -> dict[str, Any]:
        return {
            **CHAT_COMPLETION_KWARGS,
            "max_tokens": completion_max_tokens_for_items(
                ANSWER_STEP_TOKEN_BUDGET,
                len(self._questions),
            ),
        }

    def structured_json_format(self) -> str:
        return (
            "{\n"
            '  "answers": [\n'
            '    {"answer": "...", "explanation": "..."},\n'
            "    ...\n"
            "  ]\n"
            "}"
        )

    def build_messages(self) -> list[dict[str, Any]]:
        n = len(self._questions)
        numbered = "\n".join(
            f"{i + 1}. {text}" for i, text in enumerate(self._questions)
        )
        user_prompt = (
            f"Solve each question below. Return exactly {n} objects in `answers`, in the same order as listed.\n\n"
            f"Questions:\n{numbered}\n\n"
            "The `answer` field must be the exact final result only—no steps or commentary there. "
            "Put all reasoning, derivation, and calculations in `explanation`.\n\n"
            f"{JSON_OUTPUT_REMINDER}"
        )
        return [
            {
                "role": "system",
                "content": self._system_prompt(
                    requirements=self._requirements,
                    chain_of_thought=ANSWER_GENERATOR_CHAIN_OF_THOUGHT,
                ),
            },
            {"role": "user", "content": user_prompt},
        ]

    def parse(self, raw: str) -> GeneratedAnswersPayload:
        result = super().parse(raw)
        if len(result.answers) != len(self._questions):
            raise ValueError(
                f"Expected {len(self._questions)} answers, got {len(result.answers)}",
            )
        return result
