"""Generation LLM task implementations (full quiz, single MCQ)."""

from app.modules.generation.llm.full_quiz import FullQuizLlm
from app.modules.generation.llm.single_mcq import SINGLE_MCQ_MAX_TOKENS, SingleMcqLlm

__all__ = [
    "FullQuizLlm",
    "SINGLE_MCQ_MAX_TOKENS",
    "SingleMcqLlm",
]
