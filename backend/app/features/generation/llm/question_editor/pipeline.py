from __future__ import annotations

from langchain_core.language_models.chat_models import BaseChatModel

from app.features.generation.llm.core import BasePipeline
from app.features.generation.llm.question_editor.generator import QuestionGenerator
from app.features.generation.models import MultipleChoiceQuestion


class QuestionPipeline(BasePipeline[MultipleChoiceQuestion]):
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

    async def _run(self, model: str, llm: BaseChatModel) -> MultipleChoiceQuestion:
        question_generator = QuestionGenerator(
            self._topic, self._question, self._comment
        )
        return await self._run_generator_step(
            question_generator,
            model,
            llm,
        )
