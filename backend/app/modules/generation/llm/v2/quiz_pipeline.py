"""Multi-step quiz generation: stems → answers → distractors → `Quiz` with shuffled options."""

from __future__ import annotations

from openai import AsyncOpenAI

from app.modules.generation.config import prompts
from app.modules.generation.config.mc_question import MC_QUESTION_OPTION_COUNT_DEFAULT
from app.modules.generation.models import MultipleChoiceQuestion, Quiz, TokenUsage
from app.modules.generation.config.prompts import USER_INSTRUCTIONS_FORMATTER
from app.modules.generation.helpers.options import shuffle_option_order
from app.modules.generation.helpers.question_data import format_topic
from app.modules.generation.llm.core import BaseQuizPipeline
from app.modules.generation.llm.v2.generators.answer import AnswerGenerator
from app.modules.generation.llm.v2.generators.distractor import DistractorGenerator
from app.modules.generation.llm.v2.generators.question import QuestionGenerator


class FullQuizV2Pipeline(BaseQuizPipeline):
    """Runs question → answer → distractor steps and returns ``Quiz``."""

    async def run(self, model: str, client: AsyncOpenAI) -> tuple[Quiz, TokenUsage]:
        t = self._topic.strip()
        context_blk = (
            format_topic(self._topic)
            if t
            else "The user did not provide a topic."
        )

        constraints_blk = getattr(self._question_class, "constraints", "")
        if self._user_instructions:
            constraints_blk = (
                f"{constraints_blk}\n"
                f"{USER_INSTRUCTIONS_FORMATTER.format_section(self._user_instructions)}"
            )

        question_generator = QuestionGenerator(
            topic=self._topic,
            num_questions=self._num_questions,
            few_shot_examples=self._few_shot_examples,
            guidelines=prompts.QUIZ_SOURCE_PRIORITY_GUIDANCE,
            constraints=constraints_blk,
            context=context_blk,
            chain_of_thought=getattr(self._question_class, "chain_of_thought", ""),
        )
        stems_payload, usage = await self._run_generator_step(
            question_generator,
            model,
            client,
            usage_before_step=None,
        )

        answer_generator = AnswerGenerator(questions=stems_payload.questions)
        answers_payload, usage = await self._run_generator_step(
            answer_generator,
            model,
            client,
            usage_before_step=usage,
        )

        distractor_generator = DistractorGenerator(
            questions=stems_payload.questions,
            solved=answers_payload.answers,
            num_distractors=MC_QUESTION_OPTION_COUNT_DEFAULT - 1,
        )
        distractors_payload, usage = await self._run_generator_step(
            distractor_generator,
            model,
            client,
            usage_before_step=usage,
        )

        built: list[MultipleChoiceQuestion] = []
        for stem, ans, row in zip(
            stems_payload.questions,
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
