"""Single-call question generation: one JSON-mode completion returning a single ``MultipleChoiceQuestion``."""

from __future__ import annotations

from app.integrations.openai.client import OpenAiChat
from app.modules.generation.llm.core import BasePipeline
from app.modules.generation.llm.v1.single_mcq import SingleQuestionGenerator
from app.modules.generation.models import MultipleChoiceQuestion


class QuestionPipeline(BasePipeline[MultipleChoiceQuestion]):
    """Runs monolithic :class:`SingleQuestionGenerator` (one completion that returns a single question JSON)."""

    def __init__(
        self,
        topic: str,
        question: MultipleChoiceQuestion,
        comment: str,
    ) -> None:
        super().__init__()
        self._topic = topic
        self._question = question
        self._comment = comment

    async def _run(self, model: str, llm: OpenAiChat) -> MultipleChoiceQuestion:
        question_generator = SingleQuestionGenerator(
            self._topic, self._question, self._comment
        )
        return await self._run_generator_step(
            question_generator,
            model,
            llm,
        )
