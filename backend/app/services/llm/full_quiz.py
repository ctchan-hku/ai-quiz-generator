"""Full-quiz LLM: `POST /api/generate/text` — topic → completion → `QuizSchema` via `FullQuizLlm.parse`."""

import json
from typing import Any

from app.models.schemas import MultipleChoiceQuestion, Quiz
from app.services.few_shot import format_few_shot_system_section
from app.services.parser import strip_fences
from app.services import prompts
from app.services.llm.core.bases import BaseChatGeneration, BaseLlmJsonParse
from app.helpers.question_data import question_type_literal


class FullQuizLlm(BaseChatGeneration, BaseLlmJsonParse[Quiz]):
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

    def build_messages(self) -> list[dict[str, Any]]:
        qtype = question_type_literal(self._question_class)
        full_system_prompt = (
            f"{prompts.ROLE_DEFINITION}\n\n"
            f"{self._outline()}\n\n"
            f"{self._question_class.instructions}"
        )
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

    def _outline(self) -> str:
        """JSON root shape required by the prompt"""
        return (
            "**JSON output**\n"
            f'- Root object must be exactly {{"questions": [<{self._num_questions} question objects>]}}.\n'
            "- Do not use a bare array or a single question object at the root."
        )

    def parse(self, raw: str) -> Quiz:
        """Turn assistant text into `QuizSchema` (bare list or `questions` key)."""
        result = json.loads(strip_fences(raw))
        if isinstance(result, list):
            data = {"questions": result}
        elif isinstance(result, dict) and "questions" in result:
            data = result
        else:
            raise ValueError("Unexpected LLM output shape")
        return Quiz.model_validate(data)
