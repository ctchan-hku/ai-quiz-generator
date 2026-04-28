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

    def output_format(self) -> str:
        return (
            "JSON Prompting: A structured schema ensures output like:\n"
            "{\n"
            f'  "questions": [ ... exactly {self._num_questions} question objects ... ]\n'
            "}\n"
            "No ambiguity. No parsing headaches. Production-ready."
        )

    def build_messages(self) -> list[dict[str, Any]]:
        qtype = question_type_literal(self._question_class)
        
        task_blk = (
            f"Create a quiz with {self._num_questions} {qtype} questions.\n"
            f"Subject-matter scope (what the quiz should cover): {self._topic}"
        )
        
        constraints_blk = getattr(self._question_class, "constraints", "")
        if self._user_instructions:
            constraints_blk = (
                f"{constraints_blk.rstrip()}\n\n"
                f"{USER_INSTRUCTIONS_FORMATTER.format_section(self._user_instructions)}"
            )
            
        examples_blk = ""
        if self._few_shot_examples:
            examples_blk = FEW_SHOT_FORMATTER.format_section(self._few_shot_examples)

        chain_of_thought_blk = getattr(self._question_class, "chain_of_thought", "")

        full_system_prompt = self._system_prompt(
            task=task_blk,
            constraints=constraints_blk,
            examples=examples_blk,
            chain_of_thought=chain_of_thought_blk,
        )

        user_content = "Please generate the quiz now according to the system prompt."

        return [
            {"role": "system", "content": full_system_prompt},
            {"role": "user", "content": user_content},
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
