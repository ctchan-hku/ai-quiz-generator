from __future__ import annotations

from typing import Any, ClassVar

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.features.generation.llm.shared.prompts import (
    FEW_SHOT_FORMATTER,
    USER_INSTRUCTIONS_FORMATTER,
)
from app.features.generation.llm.v2.generators.difficulty_target.prompts import (
    CHAIN_OF_THOUGHT,
    GUIDELINES,
    ROLE,
    STRUCTURED_JSON_FORMAT,
    USER_PROMPT,
)
from app.integrations.langchain.structured_step import StructuredLlmStep


class DifficultyTargetPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    difficulty_index: float = Field(ge=0.0, le=1.0)

    @field_validator("difficulty_index", mode="before")
    @classmethod
    def coerce_difficulty_index(cls, value: object) -> object:
        if isinstance(value, str):
            return float(value.strip())
        return value


class DifficultyTargetGenerator(StructuredLlmStep[DifficultyTargetPayload]):
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
        return ROLE

    def structured_json_format(self) -> str:
        return STRUCTURED_JSON_FORMAT

    def build_messages(self) -> list[dict[str, Any]]:
        return [
            {
                "role": "system",
                "content": self._system_prompt(
                    guidelines=GUIDELINES,
                    requirements=self._requirements,
                    examples=self._examples,
                    chain_of_thought=CHAIN_OF_THOUGHT,
                ),
            },
            {"role": "user", "content": USER_PROMPT},
        ]
