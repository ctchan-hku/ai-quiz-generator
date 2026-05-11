"""LLM step: generate question stems from topic, count, and optional few-shot lines (JSON only)."""

from typing import Any, ClassVar

from pydantic import BaseModel, ConfigDict

from app.modules.generation.config.prompts import FEW_SHOT_FORMATTER
from app.modules.generation.llm.core.llm_json_generator import LlmJsonGenerator
from app.modules.generation.llm.v2.config.completion_tokens import (
    QUESTION_STEP_TOKEN_BUDGET,
    completion_max_tokens_for_items,
)
from app.modules.generation.llm.v2.config.prompt import (
    QUESTION_GENERATOR_FEW_SHOT_USER_APPEND,
    QUESTION_GENERATOR_ROLE_DEFAULT,
)
from app.modules.generation.services.prompter import CHAT_COMPLETION_KWARGS


class GeneratedQuestionsPayload(BaseModel):
    """JSON object from the question generator (stems only, no answers)."""

    model_config = ConfigDict(extra="forbid")

    questions: list[str]


class QuestionGenerator(LlmJsonGenerator[GeneratedQuestionsPayload]):
    """Produce a list of question stems from few-shot lines, topic, and desired count."""

    parse_response_model: ClassVar[type[GeneratedQuestionsPayload]] = GeneratedQuestionsPayload

    def __init__(
        self,
        *,
        topic: str,
        num_questions: int,
        few_shot_examples: list[str] | None = None,
        constraints: str = "",
    ) -> None:
        if num_questions < 1:
            raise ValueError("num_questions must be at least 1")
        self._topic = topic.strip()
        self._num_questions = num_questions
        self._constraints = constraints
        self._few_shot_section = (
            FEW_SHOT_FORMATTER.format_section(few_shot_examples)
            if few_shot_examples
            else ""
        )

    @property
    def role_definition(self) -> str:
        return QUESTION_GENERATOR_ROLE_DEFAULT

    @property
    def _chat_completion(self) -> dict[str, Any]:
        return {
            **CHAT_COMPLETION_KWARGS,
            "max_tokens": completion_max_tokens_for_items(
                QUESTION_STEP_TOKEN_BUDGET,
                self._num_questions,
            ),
        }

    def structured_json_format(self) -> str:
        return '{\n  "questions": ["...", "..."]\n}'

    def build_messages(self) -> list[dict[str, Any]]:
        topic_line = self._topic if self._topic else "(unspecified topic)"
        user_prompt = (
            f"Task: Create exactly {self._num_questions} question stems on topic: {topic_line}. "
            "Output only the question stems in JSON as specified — no answers, options, or explanations."
        )
        if self._few_shot_section:
            user_prompt += QUESTION_GENERATOR_FEW_SHOT_USER_APPEND
        return [
            {
                "role": "system",
                "content": self._system_prompt(
                    constraints=self._constraints,
                    examples=self._few_shot_section,
                ),
            },
            {"role": "user", "content": user_prompt},
        ]

    def parse(self, raw: str) -> GeneratedQuestionsPayload:
        result = super().parse(raw)
        if len(result.questions) != self._num_questions:
            raise ValueError(
                f"Expected {self._num_questions} questions, got {len(result.questions)}",
            )
        return result
