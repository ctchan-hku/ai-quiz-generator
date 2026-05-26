from __future__ import annotations

from typing import Any, ClassVar

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.modules.generation.config.prompts import (
    FEW_SHOT_FORMATTER,
    JSON_OUTPUT_REMINDER,
    USER_INSTRUCTIONS_FORMATTER,
)
from app.modules.generation.llm.core.llm_json_generator import LlmJsonGenerator
from app.modules.generation.llm.v2.config.completion_tokens import (
    DIFFICULTY_TARGET_TOKEN_BUDGET,
)
from app.modules.generation.llm.v2.config.prompt import (
    DIFFICULTY_TARGET_CHAIN_OF_THOUGHT,
    DIFFICULTY_TARGET_GUIDELINES,
    DIFFICULTY_TARGET_ROLE_DEFAULT,
    difficulty_target_structured_json_format,
)


class DifficultyTargetPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    difficulty_index: float = Field(ge=0.0, le=1.0)

    @field_validator("difficulty_index", mode="before")
    @classmethod
    def coerce_difficulty_index(cls, value: object) -> object:
        if isinstance(value, str):
            return float(value.strip())
        return value


class DifficultyTargetGenerator(LlmJsonGenerator[DifficultyTargetPayload]):
    parse_response_model: ClassVar[type[DifficultyTargetPayload]] = (
        DifficultyTargetPayload
    )

    def __init__(
        self,
        *,
        user_instructions: list[str] | None = None,
        few_shot_examples: list[str] | None = None,
    ) -> None:
        self._requirements = USER_INSTRUCTIONS_FORMATTER.format_section(
            user_instructions,
        )
        self._examples = FEW_SHOT_FORMATTER.format_section(few_shot_examples)

    @property
    def role_definition(self) -> str:
        return DIFFICULTY_TARGET_ROLE_DEFAULT

    def completion_max_tokens(self) -> int:
        return DIFFICULTY_TARGET_TOKEN_BUDGET.max_tokens(1)

    def structured_json_format(self) -> str:
        return difficulty_target_structured_json_format()

    def build_messages(self) -> list[dict[str, Any]]:
        user_prompt = (
            "Task: Determine the single target difficulty index for new questions "
            "based on the user instructions and few-shot examples in the system message.\n\n"
            'Return exactly one JSON object with one numeric field `"difficulty_index"` '
            "between 0.0 and 1.0 inclusive. Do not quote the number as a string.\n\n"
            f"{JSON_OUTPUT_REMINDER}"
        )
        return [
            {
                "role": "system",
                "content": self._system_prompt(
                    guidelines=DIFFICULTY_TARGET_GUIDELINES,
                    requirements=self._requirements,
                    examples=self._examples,
                    chain_of_thought=DIFFICULTY_TARGET_CHAIN_OF_THOUGHT,
                ),
            },
            {"role": "user", "content": user_prompt},
        ]
