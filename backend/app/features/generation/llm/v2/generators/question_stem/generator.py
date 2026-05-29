from typing import Any, ClassVar

from pydantic import BaseModel, ConfigDict

from app.integrations.langchain.structured_step import StructuredLlmStep
from app.features.generation.llm.shared.prompts import FEW_SHOT_FORMATTER
from app.features.generation.llm.v2.generators.question_stem.prompts import (
    CHAIN_OF_THOUGHT,
    ROLE,
    STRUCTURED_JSON_FORMAT,
    USER_DIFFICULTY_NOTE,
    USER_FEW_SHOT_NOTE,
    USER_PROMPT,
)


class StemsPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    stems: list[str]


class QuestionStemGenerator(StructuredLlmStep[StemsPayload]):
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
        return ROLE

    def structured_json_format(self) -> str:
        return STRUCTURED_JSON_FORMAT

    def build_messages(self) -> list[dict[str, Any]]:
        topic_line = self._topic if self._topic else "(unspecified topic)"
        user_prompt = USER_PROMPT.format(
            num_stems=self._num_stems,
            topic_line=topic_line,
        )
        if self._few_shot_section:
            user_prompt += USER_FEW_SHOT_NOTE
        if self._difficulty_context:
            user_prompt += USER_DIFFICULTY_NOTE
        system_sections: dict[str, str] = {
            "requirements": self._requirements,
            "examples": self._few_shot_section,
            "context": self._difficulty_context,
        }
        if self._difficulty_context:
            system_sections["chain_of_thought"] = CHAIN_OF_THOUGHT
        return [
            {
                "role": "system",
                "content": self._system_prompt(**system_sections),
            },
            {"role": "user", "content": user_prompt},
        ]

    def post_process(self, result: StemsPayload) -> StemsPayload:
        if len(result.stems) != self._num_stems:
            raise ValueError(
                f"Expected {self._num_stems} question stems, got {len(result.stems)}",
            )
        return result
