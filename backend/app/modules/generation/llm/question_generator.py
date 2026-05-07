"""LLM step: generate question stems from topic, count, and optional example questions (JSON only)."""

from typing import Any, ClassVar

from pydantic import BaseModel, ConfigDict

from app.modules.generation.services.parser import BaseLlmJsonParse
from app.modules.generation.services.prompter import CHAT_COMPLETION_KWARGS, JsonResponsePrompter

QUESTION_GENERATOR_ROLE_DEFAULT = (
    "You design assessment questions that measure how well students understand a topic. "
    "Use whatever question style fits the examples and topic; you are not limited to multiple choice."
)

_BASE_STEM_TOKENS = 400
_PER_QUESTION_STEM_TOKENS = 180


def _max_tokens_for_count(num_questions: int) -> int:
    return min(4096, _BASE_STEM_TOKENS + _PER_QUESTION_STEM_TOKENS * num_questions)


class GeneratedQuestionsPayload(BaseModel):
    """JSON object from the question generator (stems only, no answers)."""

    model_config = ConfigDict(extra="forbid")

    questions: list[str]


class QuestionGeneratorLlm(JsonResponsePrompter, BaseLlmJsonParse[GeneratedQuestionsPayload]):
    """Produce a list of question stems from few-shot examples, topic, and desired count."""

    parse_response_model: ClassVar[type[GeneratedQuestionsPayload]] = GeneratedQuestionsPayload

    def __init__(
        self,
        *,
        topic: str,
        num_questions: int,
        few_shot_examples: list[str] | None = None,
    ) -> None:
        if num_questions < 1:
            raise ValueError("num_questions must be at least 1")
        self._topic = topic.strip()
        self._num_questions = num_questions
        self._few_shot_examples = few_shot_examples if few_shot_examples is not None else []

    @property
    def role_definition(self) -> str:
        return QUESTION_GENERATOR_ROLE_DEFAULT

    @property
    def _chat_completion(self) -> dict[str, Any]:
        return {
            **CHAT_COMPLETION_KWARGS,
            "max_tokens": _max_tokens_for_count(self._num_questions),
        }

    def structured_json_format(self) -> str:
        return '{\n  "questions": ["...", "..."]\n}'

    def build_messages(self) -> list[dict[str, Any]]:
        examples_text = (
            "\n".join(self._few_shot_examples)
            if self._few_shot_examples
            else "(No examples provided.)"
        )
        topic_line = self._topic if self._topic else "(unspecified topic)"
        user_prompt = f"""Given these example questions:
{examples_text}

Generate {self._num_questions} similar questions on topic: {topic_line}
Output only the question stems in JSON as specified — no answers, options, or explanations."""
        return [
            {"role": "system", "content": self._system_prompt()},
            {"role": "user", "content": user_prompt},
        ]

    def parse(self, raw: str) -> GeneratedQuestionsPayload:
        result = super().parse(raw)
        if len(result.questions) != self._num_questions:
            raise ValueError(
                f"Expected {self._num_questions} questions, got {len(result.questions)}",
            )
        return result
