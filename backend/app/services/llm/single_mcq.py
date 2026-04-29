import json
from typing import Any

from app.models.schemas import MultipleChoiceQuestion
from app.services.parser import strip_fences
from app.services import prompts
from app.services.llm.core.bases import BaseChatGeneration, BaseLlmJsonParse
from app.services.llm.openai.client import CHAT_COMPLETION_KWARGS
from app.helpers.options import shuffle_option_order
from app.helpers.question_data import format_question

SINGLE_MCQ_MAX_TOKENS = 1400


class SingleMcqLlm(BaseChatGeneration, BaseLlmJsonParse[MultipleChoiceQuestion]):
    """
    Endpoint handler for `POST /api/generate/question` that generates 
    a single multiple-choice question in `MultipleChoiceQuestion` format.
    """

    @property
    def role_definition(self) -> str:
        return (
            "You are an expert quiz editor specializing in refining a single multiple-choice "
            "question so it stays high-quality, factually accurate, and aligned with the quiz "
            "topic, constraints, and any editor feedback."
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

    def output_format(self) -> str:
        return (
            "JSON Prompting: A structured schema ensures output like:\n\n"
            "{\n"
            '  "question_type": "multiple_choice",\n'
            '  "question": "...",\n'
            '  "options": ["...", "...", "...", "..."],\n'
            '  "correct_indices": [0],\n'
            '  "explanation": "..."\n'
            "}\n\n"
            "options: 2–6 strings (default four). correct_indices: one or more distinct valid indices.\n\n"
            "No ambiguity. No parsing headaches. Production-ready."
        )

    def build_messages(self) -> list[dict[str, Any]]:
        feedback = (
            f"Editor comment:\n{self._comment}"
            if self._comment
            else prompts.REWRITE_HINT
        )
        task_blk = (
            f"Improve and rewrite a single multiple choice question.\n"
            f"Quiz topic: {self._topic}\n\n"
            f"Target question to improve:\n{format_question(self._question)}\n\n"
            f"{feedback}"
        )
        
        full_system_prompt = self._system_prompt(
            task=task_blk,
            constraints=getattr(MultipleChoiceQuestion, "constraints", ""),
        )

        user_content = "Please generate the improved question now according to the system prompt."

        return [
            {"role": "system", "content": full_system_prompt},
            {"role": "user", "content": user_content},
        ]

    def parse(self, raw: str) -> MultipleChoiceQuestion:
        result = json.loads(strip_fences(raw))
        if not isinstance(result, dict):
            raise ValueError("Expected a JSON object for one MCQ")
        mcq = MultipleChoiceQuestion.model_validate(result)
        new_options, new_correct = shuffle_option_order(mcq.options, mcq.correct_indices)
        return mcq.model_copy(update={"options": new_options, "correct_indices": new_correct})
