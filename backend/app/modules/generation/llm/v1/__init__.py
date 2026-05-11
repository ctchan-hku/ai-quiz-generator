"""Version 1 LLMs: monolithic full quiz and single-MCQ refinement."""

from app.modules.generation.llm.v1.full_quiz import FullQuizGenerator, QUIZ_AUTHOR_ROLE_DEFAULT
from app.modules.generation.llm.v1.quiz_pipeline import FullQuizV1Pipeline
from app.modules.generation.llm.v1.single_mcq import SINGLE_MCQ_MAX_TOKENS, SingleQuestionGenerator

__all__ = [
    "FullQuizGenerator",
    "FullQuizV1Pipeline",
    "QUIZ_AUTHOR_ROLE_DEFAULT",
    "SINGLE_MCQ_MAX_TOKENS",
    "SingleQuestionGenerator",
]
