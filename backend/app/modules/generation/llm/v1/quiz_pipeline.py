"""Single-call quiz generation: one JSON-mode completion returning a full ``Quiz``."""

from __future__ import annotations

from openai import AsyncOpenAI

from app.models.mc_question import MultipleChoiceQuestion
from app.models.quiz import Quiz
from app.models.token_usage import TokenUsage
from app.modules.generation.llm.v1.full_quiz import FullQuizLlm


class FullQuizV1Pipeline:
    """Runs monolithic :class:`FullQuizLlm` (one completion that returns the full quiz JSON)."""

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

    async def run(self, model: str, client: AsyncOpenAI) -> tuple[Quiz, TokenUsage]:
        task = FullQuizLlm(
            self._topic,
            self._num_questions,
            question_class=self._question_class,
            few_shot_examples=self._few_shot_examples,
            user_instructions=self._user_instructions,
        )
        raw, messages, usage_first = await task.generate(model, client)
        return await task.parse_with_retry(
            raw,
            client,
            messages,
            model=model,
            initial_usage=usage_first,
        )
