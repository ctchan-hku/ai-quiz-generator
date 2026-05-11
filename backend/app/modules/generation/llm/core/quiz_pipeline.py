"""Shared quiz pipeline construction and per-step ``generate`` → ``parse_with_retry`` orchestration."""

from __future__ import annotations

from typing import TypeVar

from openai import AsyncOpenAI
from pydantic import BaseModel

from app.models.mc_question import MultipleChoiceQuestion
from app.models.token_usage import TokenUsage, add_usage
from app.modules.generation.config.prompts import FEW_SHOT_FORMATTER, USER_INSTRUCTIONS_FORMATTER
from app.modules.generation.llm.core.llm_json_generator import LlmJsonGenerator

TStep = TypeVar("TStep", bound=BaseModel)


class BaseQuizPipeline:
    """Normalized quiz inputs plus one LLM JSON generation step (generate → parse with retry, usage folded in)."""

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
        self._few_shot_examples = FEW_SHOT_FORMATTER.normalize(few_shot_examples)
        self._user_instructions = USER_INSTRUCTIONS_FORMATTER.normalize(user_instructions)

    async def _run_generator_step(
        self,
        generator: LlmJsonGenerator[TStep],
        model: str,
        client: AsyncOpenAI,
        *,
        usage_before_step: TokenUsage | None,
    ) -> tuple[TStep, TokenUsage]:
        raw, messages, gen_usage = await generator.generate(model, client)
        initial_usage = (
            gen_usage.model_copy()
            if usage_before_step is None
            else add_usage(usage_before_step.model_copy(), gen_usage)
        )
        return await generator.parse_with_retry(
            raw,
            client,
            messages,
            model=model,
            initial_usage=initial_usage,
        )
