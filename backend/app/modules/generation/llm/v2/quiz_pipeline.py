"""Multi-step quiz generation: stems → answers → distractors → `Quiz` with shuffled options."""

from __future__ import annotations

from openai import AsyncOpenAI

from app.constants import prompts
from app.constants.mc_question import MC_QUESTION_OPTION_COUNT_DEFAULT
from app.models.mc_question import MultipleChoiceQuestion
from app.models.quiz import Quiz
from app.models.token_usage import TokenUsage, add_usage
from app.modules.generation.config.prompts import USER_INSTRUCTIONS_FORMATTER
from app.modules.generation.helpers.options import shuffle_option_order
from app.modules.generation.helpers.question_data import format_topic
from app.modules.generation.llm.v2.answer_deriver import AnswerDeriverLlm
from app.modules.generation.llm.v2.distractor_generator import DistractorGeneratorLlm
from app.modules.generation.llm.v2.question_generator import QuestionGeneratorLlm
from app.modules.generation.services.prompter import JsonResponsePrompter


def _chat_completion(model: str, task: JsonResponsePrompter) -> dict:
    return {"model": model, **task._chat_completion}


class FullQuizV2Pipeline:
    """Constructor matches the former monolithic full-quiz LLM; runs question → answer → distractor steps and returns ``Quiz``."""

    def __init__(
        self,
        topic: str,
        num_questions: int,
        question_class: type[MultipleChoiceQuestion] = MultipleChoiceQuestion,
        few_shot_examples: list[str] | None = None,
        user_instructions: list[str] | None = None,
    ) -> None:
        self._topic = topic
        self._num_questions = num_questions
        self._question_class = question_class
        self._few_shot_examples = few_shot_examples
        self._user_instructions = user_instructions if user_instructions is not None else []

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
        raw_q, msgs_q, u_q = await q_task.generate(model, client)
        stems, usage = await q_task.parse_with_retry(
            raw_q,
            client,
            msgs_q,
            chat_completion_kwargs=_chat_completion(model, q_task),
            initial_usage=u_q,
        )

        a_task = AnswerDeriverLlm(questions=stems.questions)
        raw_a, msgs_a, u_a = await a_task.generate(model, client)
        usage = add_usage(usage, u_a)
        solved, usage = await a_task.parse_with_retry(
            raw_a,
            client,
            msgs_a,
            chat_completion_kwargs=_chat_completion(model, a_task),
            initial_usage=usage,
        )

        num_wrong = MC_QUESTION_OPTION_COUNT_DEFAULT - 1
        d_task = DistractorGeneratorLlm(
            questions=stems.questions,
            solved=solved.answers,
            num_distractors=num_wrong,
        )
        raw_d, msgs_d, u_d = await d_task.generate(model, client)
        usage = add_usage(usage, u_d)
        dist, usage = await d_task.parse_with_retry(
            raw_d,
            client,
            msgs_d,
            chat_completion_kwargs=_chat_completion(model, d_task),
            initial_usage=usage,
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
