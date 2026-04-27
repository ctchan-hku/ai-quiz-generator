"""Single-MCQ LLM: `POST /api/generate/question` — regen → completion → `MultipleChoiceQuestion` via `SingleMcqLlm.parse`."""

from typing import Any, ClassVar

from app.models.schemas import MultipleChoiceQuestion
from app.services.parser import LlmParseRetrySpec, load_llm_json_value, make_llm_parse_retry_spec
from app.services.llm.bases import BaseChatGeneration, BaseLlmJsonParse
from app.services.llm.common import CHAT_COMPLETION_KWARGS
from backend.app.services.helper import format_question_for_prompt

SINGLE_MCQ_MAX_TOKENS = 1400

SYSTEM_PROMPT = (
    "You are a quiz assistant. Your ONLY output must be a single raw JSON object for ONE multiple_choice question.\n"
    "The object must use exactly these keys: question_type (string \"multiple_choice\"), question (string), "
    "options (array of exactly four strings), correct_indices (array of one integer 0-3), explanation (string).\n"
    "Do not wrap the object in a \"questions\" array. Do not include markdown fences or any text outside the JSON object."
)

DEFAULT_REWRITE_HINT = (
    "1. Ensure the correct answer is factually correct and valid.\n"
    "2. Provide a clear and detailed explanation for the question."
)


class SingleMcqLlm(BaseChatGeneration, BaseLlmJsonParse[MultipleChoiceQuestion]):
    """Single-question regen workflow: id `single-question` drives chat logs and parse-retry policy."""

    WORKFLOW_ID: ClassVar[str] = "single-question"
    CORRECTIVE_FOLLOW_UP: ClassVar[str] = (
        "Return ONLY a single JSON object for one multiple_choice question. "
        "Do not use a 'questions' array. No other text."
    )

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

    @property
    def retry_spec(self) -> LlmParseRetrySpec:
        return make_llm_parse_retry_spec(
            follow_up=self.CORRECTIVE_FOLLOW_UP,
            failure_noun=self.WORKFLOW_ID,
        )

    def build_messages(self) -> list[dict[str, Any]]:
        feedback = (
            f"Editor comment:\n{self._comment}" if self._comment else DEFAULT_REWRITE_HINT
        )
        user_content = (
            f"Quiz topic: {self._topic}\n\n"
            f"Target question to improve:\n{format_question_for_prompt(self._question)}\n\n"
            f"{feedback}"
        )
        return [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ]

    def parse(self, raw: str) -> MultipleChoiceQuestion:
        """Turn assistant text into one `MultipleChoiceQuestion` (single JSON object)."""
        result = load_llm_json_value(raw)
        if not isinstance(result, dict):
            raise ValueError("Expected a JSON object for one MCQ")
        return MultipleChoiceQuestion.model_validate(result)
