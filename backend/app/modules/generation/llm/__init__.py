"""LLM task implementations — re-export v1 (monolithic) and v2 (pipeline) entry points."""

from app.modules.generation.llm.v1 import (
    FullQuizGenerator,
    QUIZ_AUTHOR_ROLE_DEFAULT,
    SINGLE_MCQ_MAX_TOKENS,
    SingleQuestionGenerator,
)
from app.modules.generation.llm.v2 import (
    ANSWER_GENERATOR_CHAIN_OF_THOUGHT,
    ANSWER_GENERATOR_ROLE_DEFAULT,
    AnswerGenerator,
    GeneratedAnswersPayload,
    DISTRACTOR_GENERATOR_CHAIN_OF_THOUGHT,
    DISTRACTOR_GENERATOR_ROLE_DEFAULT,
    GeneratedDistractorsPayload,
    DistractorGenerator,
    FullQuizV2Pipeline,
    GeneratedQuestionStemsPayload,
    INSTRUCTION_ROUTER_CHAIN_OF_THOUGHT,
    INSTRUCTION_ROUTER_ROLE_DEFAULT,
    InstructionRouterGenerator,
    QUESTION_STEM_GENERATOR_ROLE_DEFAULT,
    QuestionStemGenerator,
    RoutedUserInstructions,
)

__all__ = [
    "ANSWER_GENERATOR_CHAIN_OF_THOUGHT",
    "ANSWER_GENERATOR_ROLE_DEFAULT",
    "AnswerGenerator",
    "GeneratedAnswersPayload",
    "DISTRACTOR_GENERATOR_CHAIN_OF_THOUGHT",
    "DISTRACTOR_GENERATOR_ROLE_DEFAULT",
    "GeneratedDistractorsPayload",
    "DistractorGenerator",
    "FullQuizGenerator",
    "FullQuizV2Pipeline",
    "GeneratedQuestionStemsPayload",
    "INSTRUCTION_ROUTER_CHAIN_OF_THOUGHT",
    "INSTRUCTION_ROUTER_ROLE_DEFAULT",
    "InstructionRouterGenerator",
    "QUESTION_STEM_GENERATOR_ROLE_DEFAULT",
    "QuestionStemGenerator",
    "QUIZ_AUTHOR_ROLE_DEFAULT",
    "RoutedUserInstructions",
    "SINGLE_MCQ_MAX_TOKENS",
    "SingleQuestionGenerator",
]
