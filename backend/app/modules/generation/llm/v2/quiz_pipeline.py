"""Multi-step quiz generation: stems → answers → distractors → `Quiz` with shuffled options."""

from __future__ import annotations

from openai import AsyncOpenAI

from app.modules.generation.models import MultipleChoiceQuestion, Quiz, TokenUsage
from app.modules.generation.config.prompts import USER_INSTRUCTIONS_FORMATTER
from app.modules.generation.helpers.options import shuffle_option_order
from app.modules.generation.llm.core import BaseQuizPipeline
from app.modules.generation.llm.v2.generators.answer import AnswerGenerator
from app.modules.generation.llm.v2.generators.distractor import DistractorGenerator
from app.modules.generation.llm.v2.generators.instruction_router import InstructionRouterGenerator
from app.modules.generation.llm.v2.generators.question_stem import QuestionStemGenerator


class FullQuizV2Pipeline(BaseQuizPipeline):
    """Routes user instructions → stems → answers → distractors → ``Quiz``."""

    async def run(self, model: str, client: AsyncOpenAI) -> tuple[Quiz, TokenUsage]:
        usage: TokenUsage | None = None
        stem_requirements = ""
        answer_requirements = ""
        distractor_requirements = ""

        if self._user_instructions:
            routed, usage = await self._run_generator_step(
                InstructionRouterGenerator(user_instructions=self._user_instructions),
                model,
                client,
                usage_before_step=None,
            )
            stem_requirements = USER_INSTRUCTIONS_FORMATTER.format_section(routed.stem)
            answer_requirements = USER_INSTRUCTIONS_FORMATTER.format_section(routed.answer)
            distractor_requirements = USER_INSTRUCTIONS_FORMATTER.format_section(routed.distractor)

        question_stem_generator = QuestionStemGenerator(
            topic=self._topic,
            num_question_stems=self._num_questions,
            few_shot_examples=self._few_shot_examples,
            requirements=stem_requirements,
        )
        stem_payload, usage = await self._run_generator_step(
            question_stem_generator,
            model,
            client,
            usage_before_step=usage,
        )
        stems = stem_payload.question_stems

        answer_generator = AnswerGenerator(
            questions=stems,
            requirements=answer_requirements,
        )
        answers_payload, usage = await self._run_generator_step(
            answer_generator,
            model,
            client,
            usage_before_step=usage,
        )

        distractor_generator = DistractorGenerator(
            questions=stems,
            solved=answers_payload.answers,
            requirements=distractor_requirements,
        )
        distractors_payload, usage = await self._run_generator_step(
            distractor_generator,
            model,
            client,
            usage_before_step=usage,
        )

        built: list[MultipleChoiceQuestion] = []
        for stem, ans, row in zip(
            stems,
            answers_payload.answers,
            distractors_payload.distractor_sets,
            strict=True,
        ):
            options = [ans.answer, *row.distractors]
            mc = MultipleChoiceQuestion(
                question_type="multiple_choice",
                question=stem,
                options=options,
                correct_indices=[0],
                explanation=ans.explanation,
            )
            new_opts, new_ci = shuffle_option_order(list(mc.options), list(mc.correct_indices))
            built.append(mc.model_copy(update={"options": new_opts, "correct_indices": new_ci}))

        return Quiz(questions=built), usage
