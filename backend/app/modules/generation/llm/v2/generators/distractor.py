"""LLM step: generate incorrect MCQ options from stems plus derived answer and explanation."""

from typing import Any, ClassVar

from pydantic import BaseModel, ConfigDict

from app.modules.generation.config.mc_question import (
    MC_QUESTION_OPTION_COUNT_MAX,
    MC_QUESTION_OPTION_COUNT_MIN,
)
from app.modules.generation.llm.core.llm_json_generator import LlmJsonGenerator
from app.modules.generation.llm.v2.config.completion_tokens import (
    DISTRACTOR_STEP_TOKEN_BUDGET,
    completion_max_tokens_for_items,
)
from app.modules.generation.llm.v2.config.prompt import (
    DISTRACTOR_GENERATOR_CHAIN_OF_THOUGHT,
    DISTRACTOR_GENERATOR_ROLE_DEFAULT,
    distractor_structured_json_format,
    format_distractor_user_prompt_intro,
)
from app.modules.generation.llm.v2.generators.answer import GeneratedAnswersPayload
from app.modules.generation.services.prompter import CHAT_COMPLETION_KWARGS


class GeneratedDistractorsPayload(BaseModel):
    """Top-level JSON from the distractor generator: one row per input stem."""

    model_config = ConfigDict(extra="forbid")

    class Row(BaseModel):
        """One stem's incorrect options (same order as inputs)."""

        model_config = ConfigDict(extra="forbid")

        distractors: list[str]

    distractor_sets: list[Row]


class DistractorGenerator(LlmJsonGenerator[GeneratedDistractorsPayload]):
    """For each (stem, answer, explanation), produce wrong MC options (count from requirements or platform default)."""

    parse_response_model: ClassVar[type[GeneratedDistractorsPayload]] = GeneratedDistractorsPayload

    def __init__(
        self,
        *,
        questions: list[str],
        solved: list[GeneratedAnswersPayload.Row],
        requirements: str = "",
    ) -> None:
        if not questions:
            raise ValueError("questions must be non-empty")
        if len(questions) != len(solved):
            raise ValueError("questions and solved must have the same length")
        self._questions = questions
        self._solved = solved
        self._requirements = requirements

    @property
    def role_definition(self) -> str:
        return DISTRACTOR_GENERATOR_ROLE_DEFAULT

    @property
    def _chat_completion(self) -> dict[str, Any]:
        return {
            **CHAT_COMPLETION_KWARGS,
            "max_tokens": completion_max_tokens_for_items(
                DISTRACTOR_STEP_TOKEN_BUDGET,
                len(self._questions),
            ),
        }

    def structured_json_format(self) -> str:
        return distractor_structured_json_format()

    def build_messages(self) -> list[dict[str, Any]]:
        n = len(self._questions)
        blocks: list[str] = []
        for i, (stem, item) in enumerate(zip(self._questions, self._solved, strict=True), start=1):
            blocks.append(
                f"{i}. Question:\n{stem}\n"
                f"Correct answer (do NOT repeat this in distractors):\n{item.answer}\n"
                f"Explanation (use to infer plausible mistakes):\n{item.explanation}",
            )
        user_prompt = format_distractor_user_prompt_intro(n) + "\n\n".join(blocks)
        return [
            {
                "role": "system",
                "content": self._system_prompt(
                    requirements=self._requirements,
                    chain_of_thought=DISTRACTOR_GENERATOR_CHAIN_OF_THOUGHT,
                ),
            },
            {"role": "user", "content": user_prompt},
        ]

    def parse(self, raw: str) -> GeneratedDistractorsPayload:
        result = super().parse(raw)
        if len(result.distractor_sets) != len(self._questions):
            raise ValueError(
                f"Expected {len(self._questions)} distractor_sets, got {len(result.distractor_sets)}",
            )
        for idx, row in enumerate(result.distractor_sets):
            if not MC_QUESTION_OPTION_COUNT_MIN - 1 <= len(row.distractors) <= MC_QUESTION_OPTION_COUNT_MAX - 1:
                raise ValueError(
                    f"Item {idx}: expected {MC_QUESTION_OPTION_COUNT_MIN - 1}–{MC_QUESTION_OPTION_COUNT_MAX - 1} distractors, got {len(row.distractors)}",
                )
        return result
