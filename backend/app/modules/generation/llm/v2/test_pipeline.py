from __future__ import annotations

from app.integrations.openai.client import OpenAiChat
from app.modules.generation.config.prompts import (
    FEW_SHOT_FORMATTER,
    USER_INSTRUCTIONS_FORMATTER,
)
from app.modules.generation.helpers.options import shuffle_option_order
from app.modules.generation.llm.core import BasePipeline
from app.modules.generation.llm.v2.generators.answer import AnswerGenerator
from app.modules.generation.llm.v2.generators.distractor import DistractorGenerator
from app.modules.generation.llm.v2.generators.instruction_router import (
    InstructionRouterGenerator,
)
from app.modules.generation.llm.v2.generators.question_stem import QuestionStemGenerator
from app.modules.generation.models import MultipleChoiceQuestion, Test


class FullTestV2Pipeline(BasePipeline[Test]):
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

    async def _run(self, model: str, llm: OpenAiChat) -> Test:
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

        question_stem_generator = QuestionStemGenerator(
            topic=self._topic,
            num_stems=self._num_questions,
            few_shot_examples=self._few_shot_examples,
            requirements=stem_requirements,
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
