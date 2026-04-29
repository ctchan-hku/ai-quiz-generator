import json
from typing import Any

from app.models.schemas import MultipleChoiceQuestion, Quiz
from app.services.prompt_sections.few_shot import FEW_SHOT_FORMATTER
from app.services.parser import strip_fences
from app.services.llm.core.bases import BaseChatGeneration, BaseLlmJsonParse
from app.helpers.options import shuffle_option_order
from app.helpers.question_data import question_type_literal
from app.services.prompt_sections.user_instructions import USER_INSTRUCTIONS_FORMATTER


class FullQuizLlm(BaseChatGeneration, BaseLlmJsonParse[Quiz]):
    """
    Endpoint handler for `POST /api/generate/quiz` that generates 
    a full quiz (a collection of questions) in the `Quiz` data model.
    """

    @property
    def role_definition(self) -> str:
        return (
            "You are an expert quiz generation assistant specializing in crafting high-quality, "
            "factually accurate, and unambiguous multiple-choice questions based on the "
            "provided topic, constraints, and source material."
        )

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

    def structured_json_format(self) -> str:
        n = self._num_questions
        return (
            "{\n"
            f'  "questions": [\n'
            "    {\n"
            '      "question_type": "multiple_choice",\n'
            '      "question": "...",\n'
            '      "options": ["...", "..."],\n'
            '      "correct_indices": [0],\n'
            '      "explanation": "..."\n'
            "    }\n"
            f"    ... exactly {n} question objects in this array ...\n"
            "  ]\n"
            "}"
        )

    def build_messages(self) -> list[dict[str, Any]]:
        qtype = question_type_literal(self._question_class)
        
        scope_line = (
            f"Subject-matter scope (what the quiz should cover): {self._topic}"
            if self._topic
            else (
                "Subject-matter scope was not provided—use few-shot examples (below) "
                "and constraints as the main signal for what to assess."
            )
        )
        task_blk = (
            f"Create a quiz with {self._num_questions} {qtype} questions.\n" f"{scope_line}"
        )
        
        constraints_blk = getattr(self._question_class, "constraints", "")
        if self._user_instructions:
            constraints_blk = (
                f"{constraints_blk}\n"
                f"{USER_INSTRUCTIONS_FORMATTER.format_section(self._user_instructions)}"
            )
            
        examples_blk = ""
        if self._few_shot_examples:
            examples_blk = FEW_SHOT_FORMATTER.format_section(self._few_shot_examples)

        chain_of_thought_blk = getattr(self._question_class, "chain_of_thought", "")

        system_prompt = self._system_prompt(
            task=task_blk,
            constraints=constraints_blk,
            examples=examples_blk,
            chain_of_thought=chain_of_thought_blk,
        )

        user_prompt = "Please generate the quiz now according to the system prompt."

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

    def parse(self, raw: str) -> Quiz:
        result = json.loads(strip_fences(raw))
        if isinstance(result, list):
            data = {"questions": result}
        elif isinstance(result, dict) and "questions" in result:
            data = result
        else:
            raise ValueError("Unexpected LLM output shape")
        quiz = Quiz.model_validate(data)
        reshuffled: list[MultipleChoiceQuestion] = []
        for question in quiz.questions:
            new_options, new_correct = shuffle_option_order(
                question.options, question.correct_indices
            )
            reshuffled.append(
                question.model_copy(
                    update={"options": new_options, "correct_indices": new_correct}
                )
            )
        return Quiz(questions=reshuffled)
