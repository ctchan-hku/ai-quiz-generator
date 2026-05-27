from __future__ import annotations

from langchain_core.language_models.chat_models import BaseChatModel

from app.modules.generation.config.prompts import (
    FEW_SHOT_FORMATTER,
    USER_INSTRUCTIONS_FORMATTER,
)
from app.modules.generation.llm.core import BasePipeline
from app.modules.generation.llm.v1.test_generator import TestGenerator
from app.modules.generation.models import GeneratedTest, MultipleChoiceQuestion


class FullTestV1Pipeline(BasePipeline[GeneratedTest]):
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

    async def _run(self, model: str, llm: BaseChatModel) -> GeneratedTest:
        test_generator = TestGenerator(
            self._topic,
            self._num_questions,
            question_class=self._question_class,
            few_shot_examples=self._few_shot_examples,
            user_instructions=self._user_instructions,
        )
        return await self._run_generator_step(
            test_generator,
            model,
            llm,
        )
