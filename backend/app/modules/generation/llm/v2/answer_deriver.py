"""LLM step: derive exact answers and explanations for stems from `QuestionGeneratorLlm`."""

from typing import Any, ClassVar

from pydantic import BaseModel, ConfigDict

from app.modules.generation.services.parser import BaseLlmJsonParse
from app.modules.generation.services.prompter import CHAT_COMPLETION_KWARGS, JsonResponsePrompter

ANSWER_DERIVER_ROLE_DEFAULT = (
    "You are an expert in reasoning and solving problems. "
    "You give accurate, exact final answers and keep every derivation, step, and calculation out of the answer field."
)

ANSWER_DERIVER_CHAIN_OF_THOUGHT = """Work like an expert solver:
1) Read each question and decide what quantity or conclusion it asks for.
2) Plan the method (definitions, formulas, logic, or elimination) before computing.
3) Execute carefully; for numeric tasks show arithmetic in the explanation only, not in the answer.
4) State the `answer` as the precise result the question expects (short phrase, value, or name—no trailing reasoning).
5) Put every intermediate step, justification, and check in `explanation` so the answer line stays clean."""

_BASE_ANSWER_TOKENS = 400
_PER_QUESTION_ANSWER_TOKENS = 500


def _max_tokens_for_question_count(n: int) -> int:
    return min(4096, _BASE_ANSWER_TOKENS + _PER_QUESTION_ANSWER_TOKENS * n)


class AnswerWithExplanation(BaseModel):
    """One solved item: exact answer plus full derivation (matches one input stem)."""

    model_config = ConfigDict(extra="forbid")

    answer: str
    explanation: str


class DerivedAnswersPayload(BaseModel):
    """Top-level JSON from the answer deriver."""

    model_config = ConfigDict(extra="forbid")

    answers: list[AnswerWithExplanation]


class AnswerDeriverLlm(JsonResponsePrompter, BaseLlmJsonParse[DerivedAnswersPayload]):
    """For each question stem, produce an exact `answer` and a separate `explanation` (reasoning only)."""

    parse_response_model: ClassVar[type[DerivedAnswersPayload]] = DerivedAnswersPayload

    def __init__(self, *, questions: list[str]) -> None:
        if not questions:
            raise ValueError("questions must be non-empty")
        self._questions = questions

    @property
    def role_definition(self) -> str:
        return ANSWER_DERIVER_ROLE_DEFAULT

    @property
    def _chat_completion(self) -> dict[str, Any]:
        return {
            **CHAT_COMPLETION_KWARGS,
            "max_tokens": _max_tokens_for_question_count(len(self._questions)),
        }

    def structured_json_format(self) -> str:
        return (
            "{\n"
            '  "answers": [\n'
            '    {"answer": "...", "explanation": "..."},\n'
            "    ...\n"
            "  ]\n"
            "}"
        )

    def build_messages(self) -> list[dict[str, Any]]:
        n = len(self._questions)
        numbered = "\n".join(f"{i + 1}. {text}" for i, text in enumerate(self._questions))
        user_prompt = (
            f"Solve each question below. Return exactly {n} objects in `answers`, in the same order as listed.\n\n"
            f"Questions:\n{numbered}\n\n"
            "The `answer` field must be the exact final result only—no steps or commentary there. "
            "Put all reasoning, derivation, and calculations in `explanation`."
        )
        return [
            {
                "role": "system",
                "content": self._system_prompt(chain_of_thought=ANSWER_DERIVER_CHAIN_OF_THOUGHT),
            },
            {"role": "user", "content": user_prompt},
        ]

    def parse(self, raw: str) -> DerivedAnswersPayload:
        result = super().parse(raw)
        if len(result.answers) != len(self._questions):
            raise ValueError(
                f"Expected {len(self._questions)} answers, got {len(result.answers)}",
            )
        return result
