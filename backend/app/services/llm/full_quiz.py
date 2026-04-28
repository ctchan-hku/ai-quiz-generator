import json
from typing import Any

from app.models.schemas import MultipleChoiceQuestion, Quiz
from app.services.prompt_sections.few_shot import FEW_SHOT_FORMATTER
from app.services.parser import strip_fences
from app.services.llm.core.bases import BaseChatGeneration, BaseLlmJsonParse
from app.helpers.question_data import question_type_literal
from app.services.prompt_sections.user_instructions import USER_INSTRUCTIONS_FORMATTER


class FullQuizLlm(BaseChatGeneration, BaseLlmJsonParse[Quiz]):
    """`POST /api/generate/quiz` → `Quiz`."""

    def __init__(
        self,
        topic: str,
        num_questions: int,
        question_class: type[MultipleChoiceQuestion] = MultipleChoiceQuestion,
        few_shot_examples: list[str] | None = None,
        user_instructions: list[str] | None = None,
    ) -> None:
        self._topic = topic
        self._num_questions = num_questions
        self._question_class = question_class
        self._few_shot_examples = few_shot_examples
        self._user_instructions = user_instructions if user_instructions is not None else []

    def outline(self) -> str:
        return (
            "JSON Prompting: A structured schema ensures output like:\n\n"
            "{\n"
            f'  "questions": [ ... exactly {self._num_questions} question objects ... ]\n'
            "}\n\n"
            "No ambiguity. No parsing headaches. Production-ready."
        )

    def build_messages(self) -> list[dict[str, Any]]:
        qtype = question_type_literal(self._question_class)
        instruction_segment = self._question_class.instructions
        if self._user_instructions:
            instruction_segment = (
                f"{instruction_segment}\n\n{USER_INSTRUCTIONS_FORMATTER.format_section(self._user_instructions)}"
            )
        full_system_prompt = self._system_prompt(instruction_segment)
        if self._few_shot_examples:
            full_system_prompt = (
                f"{full_system_prompt}\n\n{FEW_SHOT_FORMATTER.format_section(self._few_shot_examples)}"
            )
        return [
            {"role": "system", "content": full_system_prompt},
            {
                "role": "user",
                "content": f"Generate {self._num_questions} {qtype} questions about: {self._topic}",
            },
        ]

    def parse(self, raw: str) -> Quiz:
        result = json.loads(strip_fences(raw))
        if isinstance(result, list):
            data = {"questions": result}
        elif isinstance(result, dict) and "questions" in result:
            data = result
        else:
            raise ValueError("Unexpected LLM output shape")
        return Quiz.model_validate(data)
