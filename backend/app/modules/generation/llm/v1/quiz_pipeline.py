"""Single-call quiz generation: one JSON-mode completion returning a full ``Quiz``."""

from __future__ import annotations

from openai import AsyncOpenAI

from app.models.quiz import Quiz
from app.models.token_usage import TokenUsage
from app.modules.generation.llm.core import BaseQuizPipeline
from app.modules.generation.llm.v1.full_quiz import FullQuizGenerator


class FullQuizV1Pipeline(BaseQuizPipeline):
    """Runs monolithic :class:`FullQuizGenerator` (one completion that returns the full quiz JSON)."""

    async def run(self, model: str, client: AsyncOpenAI) -> tuple[Quiz, TokenUsage]:
        full_quiz_generator = FullQuizGenerator(
            self._topic,
            self._num_questions,
            question_class=self._question_class,
            few_shot_examples=self._few_shot_examples,
            user_instructions=self._user_instructions,
        )
        return await self._run_generator_step(
            full_quiz_generator,
            model,
            client,
            usage_before_step=None,
        )
