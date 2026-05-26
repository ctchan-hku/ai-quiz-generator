from __future__ import annotations

import logging

from langchain_core.language_models.chat_models import BaseChatModel

from app.modules.data.student_stats.handlers.question_metrics_handler import (
    QuestionMetricsHandler,
)
from app.modules.generation.config.prompts import (
    FEW_SHOT_FORMATTER,
    USER_INSTRUCTIONS_FORMATTER,
)
from app.modules.generation.helpers.options import shuffle_option_order
from app.modules.generation.llm.core import BasePipeline
from app.modules.generation.llm.v2.generators.answer import AnswerGenerator
from app.modules.generation.llm.v2.generators.difficulty_target import (
    DifficultyTargetGenerator,
)
from app.modules.generation.llm.v2.generators.distractor import DistractorGenerator
from app.modules.generation.llm.v2.generators.instruction_router import (
    InstructionRouterGenerator,
)
from app.modules.generation.llm.v2.generators.question_stem import QuestionStemGenerator
from app.modules.generation.models import MultipleChoiceQuestion, Test
from app.modules.data.student_stats.services.question_metrics_service import (
    QuestionMetricsService,
)
from app.modules.generation.helpers.reference_selection import (
    build_reference_questions,
    format_difficulty_reference_context,
    select_closest_questions,
)

logger = logging.getLogger(__name__)


class FullTestV2Pipeline(BasePipeline[Test]):
    def __init__(
        self,
        topic: str,
        num_questions: int,
        question_class: type[MultipleChoiceQuestion] = MultipleChoiceQuestion,
        few_shot_examples: list[str] | None = None,
        user_instructions: list[str] | None = None,
        selected_test_ids: list[str] | None = None,
        question_metrics_handler: QuestionMetricsHandler | None = None,
    ) -> None:
        super().__init__()
        self._topic = topic
        self._num_questions = num_questions
        self._question_class = question_class
        self._few_shot_examples = FEW_SHOT_FORMATTER.normalize(few_shot_examples)
        self._user_instructions = USER_INSTRUCTIONS_FORMATTER.normalize(
            user_instructions
        )
        self._selected_test_ids = list(selected_test_ids or [])
        self._question_metrics_handler = question_metrics_handler
        self._question_metrics_service = QuestionMetricsService()

    async def _run(self, model: str, llm: BaseChatModel) -> Test:
        stem_requirements = ""
        answer_requirements = ""
        distractor_requirements = ""

        if self._user_instructions:
            routed = await self._run_generator_step(
                InstructionRouterGenerator(user_instructions=self._user_instructions),
                model,
                llm,
            )
            stem_requirements = USER_INSTRUCTIONS_FORMATTER.format_section(routed.stem)
            answer_requirements = USER_INSTRUCTIONS_FORMATTER.format_section(
                routed.answer
            )
            distractor_requirements = USER_INSTRUCTIONS_FORMATTER.format_section(
                routed.distractor
            )

        difficulty_context = await self._build_difficulty_context(model, llm)

        question_stem_generator = QuestionStemGenerator(
            topic=self._topic,
            num_stems=self._num_questions,
            few_shot_examples=self._few_shot_examples,
            requirements=stem_requirements,
            difficulty_context=difficulty_context,
        )
        stems_payload = await self._run_generator_step(
            question_stem_generator,
            model,
            llm,
        )
        stems = stems_payload.stems

        answer_generator = AnswerGenerator(
            stems=stems,
            requirements=answer_requirements,
        )
        answers_payload = await self._run_generator_step(
            answer_generator,
            model,
            llm,
        )

        distractor_generator = DistractorGenerator(
            stems=stems,
            answers=answers_payload.items,
            requirements=distractor_requirements,
        )
        distractors_payload = await self._run_generator_step(
            distractor_generator,
            model,
            llm,
        )

        built: list[MultipleChoiceQuestion] = []
        for stem, ans, row in zip(
            stems,
            answers_payload.items,
            distractors_payload.items,
            strict=True,
        ):
            options = [ans.answer, *row.distractors]
            mc = MultipleChoiceQuestion(
                question=stem,
                options=options,
                correct_indices=[0],
                explanation=ans.explanation,
            )
            new_opts, new_ci = shuffle_option_order(
                list(mc.options), list(mc.correct_indices)
            )
            built.append(
                mc.model_copy(update={"options": new_opts, "correct_indices": new_ci})
            )

        return Test(questions=built)

    async def _build_difficulty_context(self, model: str, llm: BaseChatModel) -> str:
        if not self._selected_test_ids:
            return ""

        if self._question_metrics_handler is None:
            logger.warning(
                "selected_test_ids provided but MongoDB is disabled; "
                "skipping difficulty-target and reference-question loading",
            )
            return ""

        target = await self._run_generator_step(
            DifficultyTargetGenerator(
                user_instructions=self._user_instructions,
                few_shot_examples=self._few_shot_examples,
            ),
            model,
            llm,
        )

        candidates = []
        for test_id in self._selected_test_ids:
            context = await self._question_metrics_handler.load_by_test_id(test_id)
            if context is None:
                continue
            candidates.extend(
                build_reference_questions(context, self._question_metrics_service),
            )

        selected = select_closest_questions(
            candidates,
            target.difficulty_index,
            limit=5,
        )
        return format_difficulty_reference_context(
            target.difficulty_index,
            selected,
        )
