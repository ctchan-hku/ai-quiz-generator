"""LLM step: generate incorrect MCQ options from stems plus derived answer and explanation."""

from typing import Any, ClassVar

from pydantic import BaseModel, ConfigDict

from app.modules.generation.config.mc_question import (
    MC_QUESTION_OPTION_COUNT_MAX,
    MC_QUESTION_OPTION_COUNT_MIN,
)
from app.modules.generation.config.prompts import JSON_OUTPUT_REMINDER
from app.modules.generation.llm.core.llm_json_generator import LlmJsonGenerator
from app.modules.generation.llm.v2.config.completion_tokens import (
    DISTRACTOR_STEP_TOKEN_BUDGET,
)
from app.modules.generation.llm.v2.config.prompt import (
    DISTRACTOR_GENERATOR_CHAIN_OF_THOUGHT,
    DISTRACTOR_GENERATOR_ROLE_DEFAULT,
    distractor_structured_json_format,
    format_distractor_user_prompt_intro,
)
from app.modules.generation.llm.v2.generators.answer import AnswersPayload


class DistractorsPayload(BaseModel):
    """Top-level JSON from the distractor generator: one row per input stem."""

    model_config = ConfigDict(extra="forbid")

    class DistractorItem(BaseModel):
        """One stem's incorrect options (same order as inputs)."""

        model_config = ConfigDict(extra="forbid")

        distractors: list[str]

    items: list[DistractorItem]


class DistractorGenerator(LlmJsonGenerator[DistractorsPayload]):
    """For each (stem, answer, explanation), produce wrong MC options (count from requirements or platform default)."""

    parse_response_model: ClassVar[type[DistractorsPayload]] = DistractorsPayload

    def __init__(
        self,
        *,
        stems: list[str],
        answers: list[AnswersPayload.AnswerItem],
        requirements: str = "",
    ) -> None:
        if not stems:
            raise ValueError("stems must be non-empty")
        if len(stems) != len(answers):
            raise ValueError("stems and answers must have the same length")
        self._stems = stems
        self._answers = answers
        self._requirements = requirements

    @property
    def role_definition(self) -> str:
        return DISTRACTOR_GENERATOR_ROLE_DEFAULT

    def completion_max_tokens(self) -> int:
        return DISTRACTOR_STEP_TOKEN_BUDGET.max_tokens(len(self._stems))

    def structured_json_format(self) -> str:
        return distractor_structured_json_format()

    def build_messages(self) -> list[dict[str, Any]]:
        n = len(self._stems)
        blocks: list[str] = []
        for i, (stem, item) in enumerate(
            zip(self._stems, self._answers, strict=True), start=1
        ):
            blocks.append(
                f"{i}. Question:\n{stem}\n"
                f"Correct answer only (omit from distractors; same format as stem expects options):\n{item.answer}\n"
                "Private derivation (infer plausible distractors silently; "
                "do not quote, summarize, or paraphrase these steps inside any distractor string):\n"
                f"{item.explanation}",
            )
        user_prompt = (
            format_distractor_user_prompt_intro(n)
            + "\n\n".join(blocks)
            + "\n\n"
            + JSON_OUTPUT_REMINDER
        )
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

    def parse(self, raw: str) -> DistractorsPayload:
        result = super().parse(raw)
        if len(result.items) != len(self._stems):
            raise ValueError(
                f"Expected {len(self._stems)} items, got {len(result.items)}",
            )
        for idx, row in enumerate(result.items):
            if (
                not MC_QUESTION_OPTION_COUNT_MIN - 1
                <= len(row.distractors)
                <= MC_QUESTION_OPTION_COUNT_MAX - 1
            ):
                raise ValueError(
                    f"Item {idx}: expected {MC_QUESTION_OPTION_COUNT_MIN - 1}–{MC_QUESTION_OPTION_COUNT_MAX - 1} distractors, got {len(row.distractors)}",
                )
        return result
