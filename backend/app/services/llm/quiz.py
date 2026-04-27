"""Full-quiz LLM: `POST /api/generate/text` — topic → completion → `QuizSchema` via `FullQuizLlm.parse`."""

from typing import Any, ClassVar

from app.models.schemas import MultipleChoiceQuestion, QuizSchema
from app.services.few_shot import format_few_shot_system_section
from app.services.parser import LlmParseRetrySpec, load_llm_json_value, make_llm_parse_retry_spec
from app.services.llm.bases import BaseChatGeneration, BaseLlmJsonParse
from app.services.llm.common import CHAT_COMPLETION_KWARGS
from app.services.helper import question_type_literal

SYSTEM_PROMPT = (
    "You are a quiz generation assistant. Your ONLY output must be a raw JSON object containing a single key "
    "'questions' that holds an array of question objects.\n"
    "Do not include markdown, explanation, or any text outside the JSON object."
)


class FullQuizLlm(BaseChatGeneration, BaseLlmJsonParse[QuizSchema]):
    """Topic full-quiz workflow: id `quiz` drives chat logs and parse-retry `failure_noun`."""

    WORKFLOW_ID: ClassVar[str] = "quiz"
    CORRECTIVE_FOLLOW_UP: ClassVar[str] = "Return ONLY the corrected JSON array, no other text."

    def __init__(
        self,
        topic: str,
        num_questions: int,
        question_class: type[MultipleChoiceQuestion] = MultipleChoiceQuestion,
        few_shot_examples: list[str] | None = None,
    ) -> None:
        self._topic = topic
        self._num_questions = num_questions
        self._question_class = question_class
        self._few_shot_examples = few_shot_examples

    @property
    def _chat_completion(self) -> dict[str, Any]:
        return CHAT_COMPLETION_KWARGS

    @property
    def retry_spec(self) -> LlmParseRetrySpec:
        return make_llm_parse_retry_spec(
            follow_up=self.CORRECTIVE_FOLLOW_UP,
            failure_noun=self.WORKFLOW_ID,
        )

    def build_messages(self) -> list[dict[str, Any]]:
        qtype = question_type_literal(self._question_class)
        full_system_prompt = f"{SYSTEM_PROMPT}\n\n{self._question_class.system_prompt}"
        if self._few_shot_examples:
            full_system_prompt = (
                f"{full_system_prompt}\n\n{format_few_shot_system_section(self._few_shot_examples)}"
            )
        return [
            {"role": "system", "content": full_system_prompt},
            {
                "role": "user",
                "content": f"Generate {self._num_questions} {qtype} questions about: {self._topic}",
            },
        ]

    def parse(self, raw: str) -> QuizSchema:
        """Turn assistant text into `QuizSchema` (bare list or `questions` key)."""
        result = load_llm_json_value(raw)
        if isinstance(result, list):
            data = {"questions": result}
        elif isinstance(result, dict) and "questions" in result:
            data = result
        else:
            raise ValueError("Unexpected LLM output shape")
        return QuizSchema.model_validate(data)
