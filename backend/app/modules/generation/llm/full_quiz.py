from typing import Any, ClassVar

from app.constants import prompts
from app.modules.generation.helpers.options import shuffle_option_order
from app.modules.generation.helpers.question_data import format_topic, question_type_literal
from app.models.mc_question import MultipleChoiceQuestion
from app.models.quiz import Quiz
from app.modules.generation.config.prompts import FEW_SHOT_FORMATTER, USER_INSTRUCTIONS_FORMATTER
from app.modules.generation.services.parser import BaseLlmJsonParse
from app.modules.generation.services.prompter import JsonResponsePrompter

QUIZ_AUTHOR_ROLE_DEFAULT = (
    "You are an expert quiz generation assistant that writes factually accurate multiple-choice questions."
)


class FullQuizLlm(JsonResponsePrompter, BaseLlmJsonParse[Quiz]):
    """
    Endpoint handler for `POST /api/generate/quiz` that generates
    a full quiz (a collection of questions) in the `Quiz` data model.
    """

    parse_response_model: ClassVar[type[Quiz]] = Quiz

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

    @property
    def role_definition(self) -> str:
        return QUIZ_AUTHOR_ROLE_DEFAULT

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

        t = self._topic.strip()
        context_blk = (
            format_topic(self._topic)
            if t
            else "The user did not provide a topic."
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
            guidelines=prompts.QUIZ_SOURCE_PRIORITY_GUIDANCE,
            context=context_blk,
            constraints=constraints_blk,
            examples=examples_blk,
            chain_of_thought=chain_of_thought_blk,
        )

        user_prompt = (
            f"Task: Create exactly {self._num_questions} {qtype} questions. "
            "Follow these sections: # Guidelines, # Context, # Constraints, # Examples, # Chain of Thought, and # Output Format."
        )
        if self._few_shot_examples:
            user_prompt += (
                " When # Examples is non-empty, treat those lines as the strongest signal for "
                "difficulty, tone, and stem structure; use the topic only as broad coverage "
                "direction — examples must not be overshadowed by topic breadth alone."
            )

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

    def parse(self, raw: str) -> Quiz:
        quiz = super().parse(raw)
        shuffled: list[MultipleChoiceQuestion] = []
        for q in quiz.questions:
            new_opts, new_ci = shuffle_option_order(list(q.options), list(q.correct_indices))
            shuffled.append(q.model_copy(update={"options": new_opts, "correct_indices": new_ci}))
        return Quiz(questions=shuffled)
