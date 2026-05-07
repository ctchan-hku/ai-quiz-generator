"""Generation LLM task implementations (full quiz, single MCQ, question generator, answer deriver)."""

from app.modules.generation.llm.answer_deriver import (
    ANSWER_DERIVER_CHAIN_OF_THOUGHT,
    ANSWER_DERIVER_ROLE_DEFAULT,
    AnswerDeriverLlm,
    AnswerWithExplanation,
    DerivedAnswersPayload,
)
from app.modules.generation.llm.full_quiz import FullQuizLlm, QUIZ_AUTHOR_ROLE_DEFAULT
from app.modules.generation.llm.question_generator import (
    QUESTION_GENERATOR_ROLE_DEFAULT,
    GeneratedQuestionsPayload,
    QuestionGeneratorLlm,
)
from app.modules.generation.llm.single_mcq import SINGLE_MCQ_MAX_TOKENS, SingleMcqLlm

__all__ = [
    "ANSWER_DERIVER_CHAIN_OF_THOUGHT",
    "ANSWER_DERIVER_ROLE_DEFAULT",
    "AnswerDeriverLlm",
    "AnswerWithExplanation",
    "DerivedAnswersPayload",
    "FullQuizLlm",
    "GeneratedQuestionsPayload",
    "QUESTION_GENERATOR_ROLE_DEFAULT",
    "QuestionGeneratorLlm",
    "QUIZ_AUTHOR_ROLE_DEFAULT",
    "SINGLE_MCQ_MAX_TOKENS",
    "SingleMcqLlm",
]
