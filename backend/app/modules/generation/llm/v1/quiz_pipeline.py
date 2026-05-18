"""Single-call quiz generation: one JSON-mode completion returning a full ``Quiz``."""

from __future__ import annotations

from app.integrations.openai.client import OpenAiChat
from app.modules.generation.config.prompts import (
    FEW_SHOT_FORMATTER,
    USER_INSTRUCTIONS_FORMATTER,
)
from app.modules.generation.llm.core import BasePipeline
from app.modules.generation.llm.v1.quiz import QuizGenerator
from app.modules.generation.models import MultipleChoiceQuestion, Quiz


class FullQuizV1Pipeline(BasePipeline[Quiz]):
    """Runs monolithic :class:`QuizGenerator` (one completion that returns the full quiz JSON)."""

    def __init__(
        self,
        topic: str,
        num_questions: int,
        question_class: type[MultipleChoiceQuestion] = MultipleChoiceQuestion,
        few_shot_examples: list[str] | None = None,
        user_instructions: list[str] | None = None,
    ) -> None:
        super().__init__()
        self._topic = topic
        self._num_questions = num_questions
        self._question_class = question_class
        self._few_shot_examples = FEW_SHOT_FORMATTER.normalize(few_shot_examples)
        self._user_instructions = USER_INSTRUCTIONS_FORMATTER.normalize(
            user_instructions
        )

    async def _run(self, model: str, llm: OpenAiChat) -> Quiz:
        quiz_generator = QuizGenerator(
            self._topic,
            self._num_questions,
            question_class=self._question_class,
            few_shot_examples=self._few_shot_examples,
            user_instructions=self._user_instructions,
        )
        return await self._run_generator_step(
            quiz_generator,
            model,
            llm,
        )
