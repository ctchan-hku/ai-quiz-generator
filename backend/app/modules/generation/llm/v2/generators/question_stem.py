from typing import Any, ClassVar

from pydantic import BaseModel, ConfigDict

from app.modules.generation.config.prompts import FEW_SHOT_FORMATTER
from app.modules.generation.llm.core.llm_json_generator import LlmJsonGenerator
from app.modules.generation.llm.v2.config.completion_tokens import (
    QUESTION_STEM_STEP_TOKEN_BUDGET,
)
from app.modules.generation.llm.v2.config.prompt import (
    QUESTION_STEM_GENERATOR_DIFFICULTY_CHAIN_OF_THOUGHT,
    QUESTION_STEM_GENERATOR_DIFFICULTY_CONTEXT_REMARK,
    QUESTION_STEM_GENERATOR_FEW_SHOT_REMARK,
    QUESTION_STEM_GENERATOR_ROLE_DEFAULT,
)


class StemsPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    stems: list[str]


class QuestionStemGenerator(LlmJsonGenerator[StemsPayload]):
    parse_response_model: ClassVar[type[StemsPayload]] = StemsPayload

    def __init__(
        self,
        *,
        topic: str,
        num_stems: int,
        few_shot_examples: list[str] | None = None,
        requirements: str = "",
        difficulty_context: str = "",
    ) -> None:
        if num_stems < 1:
            raise ValueError("num_stems must be at least 1")
        self._topic = topic.strip()
        self._num_stems = num_stems
        self._requirements = requirements
        self._difficulty_context = difficulty_context.strip()
        self._few_shot_section = (
            FEW_SHOT_FORMATTER.format_section(few_shot_examples)
            if few_shot_examples
            else ""
        )

    @property
    def role_definition(self) -> str:
        return QUESTION_STEM_GENERATOR_ROLE_DEFAULT

    def completion_max_tokens(self) -> int:
        return QUESTION_STEM_STEP_TOKEN_BUDGET.max_tokens(self._num_stems)

    def structured_json_format(self) -> str:
        return '{\n  "stems": ["...", "..."]\n}'

    def build_messages(self) -> list[dict[str, Any]]:
        topic_line = self._topic if self._topic else "(unspecified topic)"
        user_prompt = (
            f"Task: Create exactly {self._num_stems} question stems on topic: {topic_line}. "
            "Output only the stems in JSON as specified — no answers, options, or explanations."
        )
        if self._few_shot_section:
            user_prompt += QUESTION_STEM_GENERATOR_FEW_SHOT_REMARK
        if self._difficulty_context:
            user_prompt += QUESTION_STEM_GENERATOR_DIFFICULTY_CONTEXT_REMARK
        system_sections: dict[str, str] = {
            "requirements": self._requirements,
            "examples": self._few_shot_section,
            "context": self._difficulty_context,
        }
        if self._difficulty_context:
            system_sections["chain_of_thought"] = (
                QUESTION_STEM_GENERATOR_DIFFICULTY_CHAIN_OF_THOUGHT
            )
        return [
            {
                "role": "system",
                "content": self._system_prompt(**system_sections),
            },
            {"role": "user", "content": user_prompt},
        ]

    def parse(self, raw: str) -> StemsPayload:
        result = super().parse(raw)
        if len(result.stems) != self._num_stems:
            raise ValueError(
                f"Expected {self._num_stems} question stems, got {len(result.stems)}",
            )
        return result
