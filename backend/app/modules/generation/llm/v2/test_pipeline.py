from __future__ import annotations

import logging

from langchain_core.language_models.chat_models import BaseChatModel

from app.core.actions.derive_question_metrics import DeriveQuestionMetricsAction
from app.modules.generation.helpers.options import shuffle_option_order
from app.modules.generation.helpers.reference_selection import (
    ReferenceQuestion,
    format_difficulty_reference_context,
    reference_questions_for_tests,
    select_closest_questions,
)
from app.modules.generation.llm.core import BasePipeline
from app.modules.generation.llm.shared.prompts import (
    FEW_SHOT_FORMATTER,
    USER_INSTRUCTIONS_FORMATTER,
)
from app.modules.generation.llm.v2.generators.answer.generator import AnswerGenerator
from app.modules.generation.llm.v2.generators.difficulty_target.generator import (
    DifficultyTargetGenerator,
)
from app.modules.generation.llm.v2.generators.distractor.generator import (
    DistractorGenerator,
)
from app.modules.generation.llm.v2.generators.instruction_router.generator import (
    InstructionRouterGenerator,
)
from app.modules.generation.llm.v2.generators.question_stem.generator import (
    QuestionStemGenerator,
)
from app.modules.generation.models import GeneratedTest, MultipleChoiceQuestion

logger = logging.getLogger(__name__)


class FullTestV2Pipeline(BasePipeline[GeneratedTest]):
    def __init__(
        self,
        topic: str,
        num_questions: int,
        question_class: type[MultipleChoiceQuestion] = MultipleChoiceQuestion,
        few_shot_examples: list[str] | None = None,
        user_instructions: list[str] | None = None,
        selected_test_ids: list[str] | None = None,
        derive_metrics_action: DeriveQuestionMetricsAction | None = None,
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
        self._derive_metrics_action = derive_metrics_action
        self._reference_questions: list[ReferenceQuestion] = []

    async def _run(self, model: str, llm: BaseChatModel) -> GeneratedTest:
        self._reference_questions = await reference_questions_for_tests(
            self._selected_test_ids,
            self._derive_metrics_action,
        )

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

        return GeneratedTest(questions=built)

    async def _build_difficulty_context(self, model: str, llm: BaseChatModel) -> str:
        if not self._reference_questions:
            return ""

        target = await self._run_generator_step(
            DifficultyTargetGenerator(
                user_instructions=self._user_instructions,
                few_shot_examples=self._few_shot_examples,
            ),
            model,
            llm,
        )

        selected = select_closest_questions(
            self._reference_questions,
            target.difficulty_index,
            limit=5,
        )
        return format_difficulty_reference_context(
            target.difficulty_index,
            selected,
        )
