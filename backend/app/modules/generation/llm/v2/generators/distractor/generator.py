from typing import Any, ClassVar

from pydantic import BaseModel, ConfigDict

from app.integrations.langchain.structured_step import StructuredLlmStep
from app.modules.generation.config.mc_question import (
    MC_QUESTION_OPTION_COUNT_MAX,
    MC_QUESTION_OPTION_COUNT_MIN,
)
from app.modules.generation.llm.v2.generators.answer.generator import AnswersPayload
from app.modules.generation.llm.v2.generators.distractor.prompts import (
    CHAIN_OF_THOUGHT,
    ROLE,
    STRUCTURED_JSON_FORMAT,
    format_user_prompt,
)


class DistractorsPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    class DistractorItem(BaseModel):
        model_config = ConfigDict(extra="forbid")

        distractors: list[str]

    items: list[DistractorItem]


class DistractorGenerator(StructuredLlmStep[DistractorsPayload]):
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
        return ROLE

    def structured_json_format(self) -> str:
        return STRUCTURED_JSON_FORMAT

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
        user_prompt = format_user_prompt(n, "\n\n".join(blocks))
        return [
            {
                "role": "system",
                "content": self._system_prompt(
                    requirements=self._requirements,
                    chain_of_thought=CHAIN_OF_THOUGHT,
                ),
            },
            {"role": "user", "content": user_prompt},
        ]

    def post_process(self, result: DistractorsPayload) -> DistractorsPayload:
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
