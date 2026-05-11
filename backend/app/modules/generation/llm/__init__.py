"""LLM task implementations — re-export v1 (monolithic) and v2 (pipeline) entry points."""

from app.modules.generation.llm.v1 import (
    FullQuizGenerator,
    QUIZ_AUTHOR_ROLE_DEFAULT,
    SINGLE_MCQ_MAX_TOKENS,
    SingleQuestionGenerator,
)
from app.modules.generation.llm.v2 import (
    ANSWER_DERIVER_CHAIN_OF_THOUGHT,
    ANSWER_DERIVER_ROLE_DEFAULT,
    AnswerGenerator,
    GeneratedAnswersPayload,
    DISTRACTOR_GENERATOR_CHAIN_OF_THOUGHT,
    DISTRACTOR_GENERATOR_ROLE_DEFAULT,
    GeneratedDistractorsPayload,
    DistractorGenerator,
    FullQuizV2Pipeline,
    GeneratedQuestionsPayload,
    QUESTION_GENERATOR_ROLE_DEFAULT,
    QuestionGenerator,
)

__all__ = [
    "ANSWER_DERIVER_CHAIN_OF_THOUGHT",
    "ANSWER_DERIVER_ROLE_DEFAULT",
    "AnswerGenerator",
    "GeneratedAnswersPayload",
    "DISTRACTOR_GENERATOR_CHAIN_OF_THOUGHT",
    "DISTRACTOR_GENERATOR_ROLE_DEFAULT",
    "GeneratedDistractorsPayload",
    "DistractorGenerator",
    "FullQuizGenerator",
    "FullQuizV2Pipeline",
    "GeneratedQuestionsPayload",
    "QUESTION_GENERATOR_ROLE_DEFAULT",
    "QuestionGenerator",
    "QUIZ_AUTHOR_ROLE_DEFAULT",
    "SINGLE_MCQ_MAX_TOKENS",
    "SingleQuestionGenerator",
]
