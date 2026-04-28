import json
from typing import Any

from app.models.schemas import MultipleChoiceQuestion
from app.services.parser import strip_fences
from app.services import prompts
from app.services.llm.core.bases import BaseChatGeneration, BaseLlmJsonParse
from app.services.llm.openai.client import CHAT_COMPLETION_KWARGS
from app.helpers.question_data import format_question

SINGLE_MCQ_MAX_TOKENS = 1400


class SingleMcqLlm(BaseChatGeneration, BaseLlmJsonParse[MultipleChoiceQuestion]):
    """`POST /api/generate/question` → `MultipleChoiceQuestion`."""

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

    def outline(self) -> str:
        return (
            "JSON Prompting: A structured schema ensures output like:\n\n"
            "{\n"
            '  "question_type": "multiple_choice",\n'
            '  "question": "...",\n'
            '  "options": ["...", "...", "...", "..."],\n'
            '  "correct_indices": [0],\n'
            '  "explanation": "..."\n'
            "}\n\n"
            "No ambiguity. No parsing headaches. Production-ready."
        )

    def build_messages(self) -> list[dict[str, Any]]:
        feedback = (
            f"Editor comment:\n{self._comment}"
            if self._comment
            else prompts.REWRITE_HINT
        )
        user_content = (
            f"Quiz topic: {self._topic}\n\n"
            f"Target question to improve:\n{format_question(self._question)}\n\n"
            f"{feedback}"
        )
        return [
            {
                "role": "system",
                "content": self._system_prompt(MultipleChoiceQuestion.instructions),
            },
            {"role": "user", "content": user_content},
        ]

    def parse(self, raw: str) -> MultipleChoiceQuestion:
        result = json.loads(strip_fences(raw))
        if not isinstance(result, dict):
            raise ValueError("Expected a JSON object for one MCQ")
        return MultipleChoiceQuestion.model_validate(result)
