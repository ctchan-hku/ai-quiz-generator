"""Full-quiz LLM: `POST /api/generate/text` — topic → completion → `QuizSchema` via `FullQuizLlm.parse`."""

from typing import Any

from app.models.schemas import MultipleChoiceQuestion, QuizSchema
from app.services.few_shot import format_few_shot_system_section
from app.services.parser import load_llm_json_value
from app.services import prompts
from app.services.llm.bases import BaseChatGeneration, BaseLlmJsonParse
from app.services.llm.common import CHAT_COMPLETION_KWARGS
from app.services.helper import question_type_literal


class FullQuizLlm(BaseChatGeneration, BaseLlmJsonParse[QuizSchema]):
    """Topic full-quiz flow: `POST /api/generate/text` → `QuizSchema`."""

    def __init__(
        self,
        topic: str,
        num_questions: int,
        question_class: type[MultipleChoiceQuestion] = MultipleChoiceQuestion,
        few_shot_examples: list[str] | None = None,
    ) -> None:
        self._topic = topic
        self._num_questions = num_questions
        self._question_class = question_class
        self._few_shot_examples = few_shot_examples

    @property
    def _chat_completion(self) -> dict[str, Any]:
        return CHAT_COMPLETION_KWARGS

    def build_messages(self) -> list[dict[str, Any]]:
        qtype = question_type_literal(self._question_class)
        full_system_prompt = f"{prompts.SYSTEM_PROMPT}\n\n{self._question_class.instructions}"
        if self._few_shot_examples:
            full_system_prompt = (
                f"{full_system_prompt}\n\n{format_few_shot_system_section(self._few_shot_examples)}"
            )
        return [
            {"role": "system", "content": full_system_prompt},
            {
                "role": "user",
                "content": f"Generate {self._num_questions} {qtype} questions about: {self._topic}",
            },
        ]

    def parse(self, raw: str) -> QuizSchema:
        """Turn assistant text into `QuizSchema` (bare list or `questions` key)."""
        result = load_llm_json_value(raw)
        if isinstance(result, list):
            data = {"questions": result}
        elif isinstance(result, dict) and "questions" in result:
            data = result
        else:
            raise ValueError("Unexpected LLM output shape")
        return QuizSchema.model_validate(data)
