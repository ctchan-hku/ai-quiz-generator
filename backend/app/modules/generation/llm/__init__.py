"""Generation LLM task implementations (full quiz, single MCQ, question generator)."""

from app.modules.generation.llm.full_quiz import FullQuizLlm, QUIZ_AUTHOR_ROLE_DEFAULT
from app.modules.generation.llm.question_generator import (
    QUESTION_GENERATOR_ROLE_DEFAULT,
    GeneratedQuestionsPayload,
    QuestionGeneratorLlm,
)
from app.modules.generation.llm.single_mcq import SINGLE_MCQ_MAX_TOKENS, SingleMcqLlm

__all__ = [
    "FullQuizLlm",
    "GeneratedQuestionsPayload",
    "QUESTION_GENERATOR_ROLE_DEFAULT",
    "QuestionGeneratorLlm",
    "QUIZ_AUTHOR_ROLE_DEFAULT",
    "SINGLE_MCQ_MAX_TOKENS",
    "SingleMcqLlm",
]
