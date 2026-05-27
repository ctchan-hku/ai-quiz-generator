from typing import Any, ClassVar

from pydantic import BaseModel, ConfigDict

from app.integrations.langchain.structured_step import StructuredLlmStep
from app.modules.generation.llm.v2.config.completion_tokens import (
    ANSWER_STEP_TOKEN_BUDGET,
)
from app.modules.generation.llm.v2.generators.answer.prompts import (
    CHAIN_OF_THOUGHT,
    ROLE,
    STRUCTURED_JSON_FORMAT,
    USER_PROMPT,
)


class AnswersPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    class AnswerItem(BaseModel):
        model_config = ConfigDict(extra="forbid")

        answer: str
        explanation: str

    items: list[AnswerItem]


class AnswerGenerator(StructuredLlmStep[AnswersPayload]):
    parse_response_model: ClassVar[type[AnswersPayload]] = AnswersPayload

    def __init__(
        self,
        *,
        stems: list[str],
        requirements: str = "",
    ) -> None:
        if not stems:
            raise ValueError("stems must be non-empty")
        self._stems = stems
        self._requirements = requirements

    @property
    def role_definition(self) -> str:
        return ROLE

    def completion_max_tokens(self) -> int:
        return ANSWER_STEP_TOKEN_BUDGET.max_tokens(len(self._stems))

    def structured_json_format(self) -> str:
        return STRUCTURED_JSON_FORMAT

    def build_messages(self) -> list[dict[str, Any]]:
        n = len(self._stems)
        numbered = "\n".join(f"{i + 1}. {text}" for i, text in enumerate(self._stems))
        user_prompt = USER_PROMPT.format(
            num_questions=n,
            numbered_questions=numbered,
        )
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

    def post_process(self, result: AnswersPayload) -> AnswersPayload:
        if len(result.items) != len(self._stems):
            raise ValueError(
                f"Expected {len(self._stems)} items, got {len(result.items)}",
            )
        return result
