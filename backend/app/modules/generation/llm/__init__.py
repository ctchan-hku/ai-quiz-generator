"""LLM task implementations — re-export v1 (monolithic) and v2 (pipeline) entry points."""

from app.modules.generation.llm.v1 import (
    QUIZ_AUTHOR_ROLE_DEFAULT,
    SINGLE_MCQ_MAX_TOKENS,
    QuizGenerator,
    QuestionGenerator,
)
from app.modules.generation.llm.v2 import (
    ANSWER_GENERATOR_CHAIN_OF_THOUGHT,
    ANSWER_GENERATOR_ROLE_DEFAULT,
    DISTRACTOR_GENERATOR_CHAIN_OF_THOUGHT,
    DISTRACTOR_GENERATOR_ROLE_DEFAULT,
    INSTRUCTION_ROUTER_CHAIN_OF_THOUGHT,
    INSTRUCTION_ROUTER_ROLE_DEFAULT,
    QUESTION_STEM_GENERATOR_ROLE_DEFAULT,
    AnswerGenerator,
    AnswersPayload,
    DistractorGenerator,
    DistractorsPayload,
    FullQuizV2Pipeline,
    InstructionRouterGenerator,
    QuestionStemGenerator,
    RoutedInstructions,
    StemsPayload,
)

__all__ = [
    "ANSWER_GENERATOR_CHAIN_OF_THOUGHT",
    "ANSWER_GENERATOR_ROLE_DEFAULT",
    "AnswerGenerator",
    "AnswersPayload",
    "DISTRACTOR_GENERATOR_CHAIN_OF_THOUGHT",
    "DISTRACTOR_GENERATOR_ROLE_DEFAULT",
    "DistractorGenerator",
    "DistractorsPayload",
    "QuizGenerator",
    "FullQuizV2Pipeline",
    "INSTRUCTION_ROUTER_CHAIN_OF_THOUGHT",
    "INSTRUCTION_ROUTER_ROLE_DEFAULT",
    "InstructionRouterGenerator",
    "QUESTION_STEM_GENERATOR_ROLE_DEFAULT",
    "QuestionStemGenerator",
    "QUIZ_AUTHOR_ROLE_DEFAULT",
    "RoutedInstructions",
    "SINGLE_MCQ_MAX_TOKENS",
    "QuestionGenerator",
    "StemsPayload",
]
