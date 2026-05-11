"""LLM step: generate question stems from topic, count, and optional example questions (JSON only)."""

from typing import Any, ClassVar

from pydantic import BaseModel, ConfigDict

from app.modules.generation.config.prompts import FEW_SHOT_FORMATTER
from app.modules.generation.llm.core.json_prompter_parse_task import JsonPrompterParseTask
from app.modules.generation.services.prompter import CHAT_COMPLETION_KWARGS

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


class QuestionGeneratorLlm(JsonPrompterParseTask[GeneratedQuestionsPayload]):
    """Produce a list of question stems from few-shot examples, topic, and desired count."""

    parse_response_model: ClassVar[type[GeneratedQuestionsPayload]] = GeneratedQuestionsPayload

    def __init__(
        self,
        *,
        topic: str,
        num_questions: int,
        few_shot_examples: list[str] | None = None,
        guidelines: str = "",
        constraints: str = "",
        context: str = "",
        examples: str | None = None,
        chain_of_thought: str = "",
    ) -> None:
        if num_questions < 1:
            raise ValueError("num_questions must be at least 1")
        self._topic = topic.strip()
        self._num_questions = num_questions
        self._guidelines = guidelines
        self._constraints = constraints
        self._context = context
        self._chain_of_thought = chain_of_thought
        if examples is not None:
            self._examples_section = examples
        elif few_shot_examples:
            self._examples_section = FEW_SHOT_FORMATTER.format_section(few_shot_examples)
        else:
            self._examples_section = ""

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
        topic_line = self._topic if self._topic else "(unspecified topic)"
        user_prompt = (
            f"Task: Create exactly {self._num_questions} question stems on topic: {topic_line}. "
            "Output only the question stems in JSON as specified — no answers, options, or explanations."
        )
        if self._examples_section:
            user_prompt += (
                " When # Examples is non-empty, treat those lines as the strongest signal for "
                "difficulty, tone, and stem structure; use the topic only as broad coverage "
                "direction — examples must not be overshadowed by topic breadth alone."
            )
        return [
            {
                "role": "system",
                "content": self._system_prompt(
                    guidelines=self._guidelines,
                    constraints=self._constraints,
                    context=self._context,
                    examples=self._examples_section,
                    chain_of_thought=self._chain_of_thought,
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
