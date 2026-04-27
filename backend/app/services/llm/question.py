"""Single-MCQ LLM: `POST /api/generate/question` — regen → completion → `MultipleChoiceQuestion` via `SingleMcqLlm.parse`."""

from typing import Any

from app.models.schemas import MultipleChoiceQuestion
from app.services.parser import load_llm_json_value
from app.services import prompts
from app.services.llm.bases import BaseChatGeneration, BaseLlmJsonParse
from app.services.llm.common import CHAT_COMPLETION_KWARGS
from app.services.helper import format_question_for_prompt

SINGLE_MCQ_MAX_TOKENS = 1400


class SingleMcqLlm(BaseChatGeneration, BaseLlmJsonParse[MultipleChoiceQuestion]):
    """Single-question regen: `POST /api/generate/question` → `MultipleChoiceQuestion`."""

    def __init__(
        self,
        topic: str,
        question: MultipleChoiceQuestion,
        comment: str | None,
    ) -> None:
        self._topic = topic
        self._question = question
        self._comment = comment

    @property
    def _chat_completion(self) -> dict[str, Any]:
        return {**CHAT_COMPLETION_KWARGS, "max_tokens": SINGLE_MCQ_MAX_TOKENS}

    def build_messages(self) -> list[dict[str, Any]]:
        feedback = (
            f"Editor comment:\n{self._comment}"
            if self._comment
            else prompts.REWRITE_HINT
        )
        user_content = (
            f"Quiz topic: {self._topic}\n\n"
            f"Target question to improve:\n{format_question_for_prompt(self._question)}\n\n"
            f"{feedback}"
        )
        return [
            {
                "role": "system",
                "content": f"{prompts.SYSTEM_PROMPT}\n\n{MultipleChoiceQuestion.instructions}",
            },
            {"role": "user", "content": user_content},
        ]

    def parse(self, raw: str) -> MultipleChoiceQuestion:
        """Turn assistant text into one `MultipleChoiceQuestion` (single JSON object)."""
        result = load_llm_json_value(raw)
        if not isinstance(result, dict):
            raise ValueError("Expected a JSON object for one MCQ")
        return MultipleChoiceQuestion.model_validate(result)
