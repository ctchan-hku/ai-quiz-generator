"""Single-call quiz generation: one JSON-mode completion returning a full ``Quiz``."""

from __future__ import annotations

from app.integrations.openai.client import OpenAiChat
from app.modules.generation.llm.core import BaseQuizPipeline
from app.modules.generation.llm.v1.full_quiz import FullQuizGenerator
from app.modules.generation.models import Quiz, TokenUsage


class FullQuizV1Pipeline(BaseQuizPipeline):
    """Runs monolithic :class:`FullQuizGenerator` (one completion that returns the full quiz JSON)."""

    async def run(self, model: str, llm: OpenAiChat) -> tuple[Quiz, TokenUsage]:
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
            llm,
            usage_before_step=None,
        )
