from typing import Any, ClassVar

from app.features.generation.helpers.options import shuffle_option_order
from app.features.generation.llm.question_editor.prompts import (
    REWRITE_HINT,
    TOPIC_CONTEXT,
    format_question_block,
)
from app.features.generation.models import MultipleChoiceQuestion
from app.integrations.langchain.structured_step import StructuredLlmStep


class QuestionGenerator(StructuredLlmStep[MultipleChoiceQuestion]):
    parse_response_model: ClassVar[type[MultipleChoiceQuestion]] = (
        MultipleChoiceQuestion
    )

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
            "You are an expert test editor specializing in refining a single multiple-choice "
            "question so it stays high-quality, factually accurate, and aligned with the test "
            "topic, requirements, and any editor feedback."
        )

    def structured_json_format(self) -> str:
        qtype = MultipleChoiceQuestion.QUESTION_TYPE_KEY
        return (
            "{\n"
            f'  "question_type": "{qtype}",\n'
            '  "question": "...",\n'
            '  "options": ["...", "...", "...", "..."],\n'
            '  "correct_indices": [0],\n'
            '  "explanation": "..."\n'
            "}"
        )

    def build_messages(self) -> list[dict[str, Any]]:
        feedback = (
            f"Editor comment:\n{self._comment}" if self._comment else REWRITE_HINT
        )
        topic = self._topic.strip()
        system_prompt = self._system_prompt(
            context=TOPIC_CONTEXT.format(topic=topic) if topic else "",
            requirements=getattr(MultipleChoiceQuestion, "guardrails", ""),
        )

        user_prompt = (
            "Task: Improve and rewrite this single multiple-choice question.\n\n"
            f"Current question:\n{format_question_block(self._question)}\n\n"
            f"{feedback}\n\n"
            "Follow the system message and output format. "
            "Reply with only the JSON object, no other text."
        )

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

    def post_process(
        self, mc_question: MultipleChoiceQuestion
    ) -> MultipleChoiceQuestion:
        new_opts, new_ci = shuffle_option_order(
            list(mc_question.options), list(mc_question.correct_indices)
        )
        return mc_question.model_copy(
            update={"options": new_opts, "correct_indices": new_ci}
        )
