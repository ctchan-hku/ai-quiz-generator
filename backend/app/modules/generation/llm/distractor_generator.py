"""LLM step: generate incorrect MCQ options from stems plus derived answer and explanation."""

from typing import Any, ClassVar

from pydantic import BaseModel, ConfigDict

from app.constants.mc_question import (
    MC_QUESTION_OPTION_COUNT_DEFAULT,
    MC_QUESTION_OPTION_COUNT_MAX,
    MC_QUESTION_OPTION_COUNT_MIN,
)
from app.modules.generation.llm.answer_deriver import AnswerWithExplanation
from app.modules.generation.services.parser import BaseLlmJsonParse
from app.modules.generation.services.prompter import CHAT_COMPLETION_KWARGS, JsonResponsePrompter

DISTRACTOR_GENERATOR_ROLE_DEFAULT = (
    "You are an expert assessment designer who writes plausible incorrect options (distractors) "
    "for multiple-choice questions. Distractors must be wrong yet tempting, and must not duplicate "
    "or paraphrase the correct answer."
)

DISTRACTOR_GENERATOR_CHAIN_OF_THOUGHT = """When inventing distractors:
1) Use the stem to judge format, domain, and difficulty (units, precision, vocabulary).
2) Use the correct answer and explanation to see common mistakes, confusions, or near-correct variants.
3) Each distractor should be incorrect but credible to a student who partially misunderstands.
4) Keep options mutually distinct; avoid absurd or joke answers unless the stem is informal.
5) Match the style and length of the correct answer (e.g. numeric vs short phrase)."""

_BASE_DISTRACTOR_TOKENS = 400
_PER_QUESTION_DISTRACTOR_TOKENS = 420


def _max_tokens_for_items(n: int) -> int:
    return min(4096, _BASE_DISTRACTOR_TOKENS + _PER_QUESTION_DISTRACTOR_TOKENS * n)


class DistractorSet(BaseModel):
    """One list of incorrect options for a single question (same order as inputs)."""

    model_config = ConfigDict(extra="forbid")

    distractors: list[str]


class DerivedDistractorsPayload(BaseModel):
    """Top-level JSON from the distractor generator."""

    model_config = ConfigDict(extra="forbid")

    distractor_sets: list[DistractorSet]


class DistractorGeneratorLlm(JsonResponsePrompter, BaseLlmJsonParse[DerivedDistractorsPayload]):
    """For each (stem, answer, explanation), produce exactly ``num_distractors`` incorrect options."""

    parse_response_model: ClassVar[type[DerivedDistractorsPayload]] = DerivedDistractorsPayload

    def __init__(
        self,
        *,
        questions: list[str],
        solved: list[AnswerWithExplanation],
        num_distractors: int = MC_QUESTION_OPTION_COUNT_DEFAULT - 1,
    ) -> None:
        if not questions:
            raise ValueError("questions must be non-empty")
        if len(questions) != len(solved):
            raise ValueError("questions and solved must have the same length")
        min_wrong = MC_QUESTION_OPTION_COUNT_MIN - 1
        max_wrong = MC_QUESTION_OPTION_COUNT_MAX - 1
        if not min_wrong <= num_distractors <= max_wrong:
            raise ValueError(
                f"num_distractors must be between {min_wrong} and {max_wrong} inclusive",
            )
        self._questions = questions
        self._solved = solved
        self._num_distractors = num_distractors

    @property
    def role_definition(self) -> str:
        return DISTRACTOR_GENERATOR_ROLE_DEFAULT

    @property
    def _chat_completion(self) -> dict[str, Any]:
        return {
            **CHAT_COMPLETION_KWARGS,
            "max_tokens": _max_tokens_for_items(len(self._questions)),
        }

    def structured_json_format(self) -> str:
        k = self._num_distractors
        return (
            "{\n"
            '  "distractor_sets": [\n'
            "    {\n"
            f'      "distractors": ["<wrong {k} options, distinct from each other and from the correct answer>"]\n'
            "    },\n"
            "    ...\n"
            "  ]\n"
            "}"
        )

    def build_messages(self) -> list[dict[str, Any]]:
        n = len(self._questions)
        k = self._num_distractors
        blocks: list[str] = []
        for i, (stem, item) in enumerate(zip(self._questions, self._solved, strict=True), start=1):
            blocks.append(
                f"{i}. Question:\n{stem}\n"
                f"Correct answer (do NOT repeat this in distractors):\n{item.answer}\n"
                f"Explanation (use to infer plausible mistakes):\n{item.explanation}",
            )
        joined = "\n\n".join(blocks)
        user_prompt = (
            f"For each numbered block above, output exactly one object in `distractor_sets` in the same order.\n"
            f"Each object's `distractors` array must contain exactly {k} strings: incorrect but plausible options.\n"
            f"There must be exactly {n} entries in `distractor_sets`.\n\n"
            f"{joined}"
        )
        return [
            {
                "role": "system",
                "content": self._system_prompt(chain_of_thought=DISTRACTOR_GENERATOR_CHAIN_OF_THOUGHT),
            },
            {"role": "user", "content": user_prompt},
        ]

    def parse(self, raw: str) -> DerivedDistractorsPayload:
        result = super().parse(raw)
        if len(result.distractor_sets) != len(self._questions):
            raise ValueError(
                f"Expected {len(self._questions)} distractor_sets, got {len(result.distractor_sets)}",
            )
        for idx, row in enumerate(result.distractor_sets):
            if len(row.distractors) != self._num_distractors:
                raise ValueError(
                    f"Item {idx}: expected {self._num_distractors} distractors, got {len(row.distractors)}",
                )
        return result
