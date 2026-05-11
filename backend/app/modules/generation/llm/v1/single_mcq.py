from typing import Any, ClassVar

from app.modules.generation.helpers.options import shuffle_option_order
from app.modules.generation.helpers.question_data import format_question, format_topic
from app.modules.generation.models import MultipleChoiceQuestion
from app.modules.generation.llm.v1.config.prompts import REWRITE_HINT
from app.modules.generation.llm.core.llm_json_generator import LlmJsonGenerator
from app.modules.generation.services.prompter import CHAT_COMPLETION_KWARGS

SINGLE_MCQ_MAX_TOKENS = 1400


class SingleQuestionGenerator(LlmJsonGenerator[MultipleChoiceQuestion]):
    """
    Endpoint handler for `POST /api/generate/question` that generates
    a single multiple-choice question in `MultipleChoiceQuestion` format.
    """

    parse_response_model: ClassVar[type[MultipleChoiceQuestion]] = MultipleChoiceQuestion

    def __init__(
        self,
        topic: str,
        question: MultipleChoiceQuestion,
        comment: str,
    ) -> None:
        self._topic = topic
        self._question = question
        self._comment = comment

    @property
    def role_definition(self) -> str:
        return (
            "You are an expert quiz editor specializing in refining a single multiple-choice "
            "question so it stays high-quality, factually accurate, and aligned with the quiz "
            "topic, requirements, and any editor feedback."
        )

    def structured_json_format(self) -> str:
        return (
            "{\n"
            '  "question_type": "multiple_choice",\n'
            '  "question": "...",\n'
            '  "options": ["...", "...", "...", "..."],\n'
            '  "correct_indices": [0],\n'
            '  "explanation": "..."\n'
            "}"
        )

    def build_messages(self) -> list[dict[str, Any]]:
        feedback = (
            f"Editor comment:\n{self._comment}"
            if self._comment
            else REWRITE_HINT
        )
        system_prompt = self._system_prompt(
            context=format_topic(self._topic),
            requirements=getattr(MultipleChoiceQuestion, "guardrails", ""),
        )

        user_prompt = (
            "Task: Improve and rewrite this single multiple-choice question.\n\n"
            f"Current question:\n{format_question(self._question)}\n\n"
            f"{feedback}\n\n"
            "Follow the system message and output format. "
            "Reply with only the JSON object, no other text."
        )

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

    def parse(self, raw: str) -> MultipleChoiceQuestion:
        mc_question = super().parse(raw)
        new_opts, new_ci = shuffle_option_order(list(mc_question.options), list(mc_question.correct_indices))
        return mc_question.model_copy(update={"options": new_opts, "correct_indices": new_ci})

    @property
    def _chat_completion(self) -> dict[str, Any]:
        return {**CHAT_COMPLETION_KWARGS, "max_tokens": SINGLE_MCQ_MAX_TOKENS}
