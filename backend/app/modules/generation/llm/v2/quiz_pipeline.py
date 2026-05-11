"""Multi-step quiz generation: stems → answers → distractors → `Quiz` with shuffled options."""

from __future__ import annotations

from openai import AsyncOpenAI

from app.constants import prompts
from app.constants.mc_question import MC_QUESTION_OPTION_COUNT_DEFAULT
from app.models.mc_question import MultipleChoiceQuestion
from app.models.quiz import Quiz
from app.models.token_usage import TokenUsage
from app.modules.generation.config.prompts import USER_INSTRUCTIONS_FORMATTER
from app.modules.generation.helpers.options import shuffle_option_order
from app.modules.generation.helpers.question_data import format_topic
from app.modules.generation.llm.core import BaseQuizPipeline
from app.modules.generation.llm.v2.answer_deriver import AnswerDeriverLlm
from app.modules.generation.llm.v2.distractor_generator import DistractorGeneratorLlm
from app.modules.generation.llm.v2.question_generator import QuestionGeneratorLlm


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

        q_task = QuestionGeneratorLlm(
            topic=self._topic,
            num_questions=self._num_questions,
            few_shot_examples=self._few_shot_examples,
            guidelines=prompts.QUIZ_SOURCE_PRIORITY_GUIDANCE,
            constraints=constraints_blk,
            context=context_blk,
            chain_of_thought=getattr(self._question_class, "chain_of_thought", ""),
        )
        stems, usage = await self._run_json_step(
            q_task,
            model,
            client,
            usage_before_step=None,
        )

        a_task = AnswerDeriverLlm(questions=stems.questions)
        solved, usage = await self._run_json_step(
            a_task,
            model,
            client,
            usage_before_step=usage,
        )

        d_task = DistractorGeneratorLlm(
            questions=stems.questions,
            solved=solved.answers,
            num_distractors=MC_QUESTION_OPTION_COUNT_DEFAULT - 1,
        )
        dist, usage = await self._run_json_step(
            d_task,
            model,
            client,
            usage_before_step=usage,
        )

        built: list[MultipleChoiceQuestion] = []
        for stem, ans, row in zip(stems.questions, solved.answers, dist.distractor_sets, strict=True):
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
