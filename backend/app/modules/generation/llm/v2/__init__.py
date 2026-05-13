"""Version 2 LLMs: multi-step quiz pipeline and per-step generators."""

from app.modules.generation.llm.v2.config.prompt import (
    ANSWER_GENERATOR_CHAIN_OF_THOUGHT,
    ANSWER_GENERATOR_ROLE_DEFAULT,
    DISTRACTOR_GENERATOR_CHAIN_OF_THOUGHT,
    DISTRACTOR_GENERATOR_ROLE_DEFAULT,
    INSTRUCTION_ROUTER_CHAIN_OF_THOUGHT,
    INSTRUCTION_ROUTER_ROLE_DEFAULT,
    QUESTION_STEM_GENERATOR_ROLE_DEFAULT,
)
from app.modules.generation.llm.v2.generators.answer import (
    AnswerGenerator,
    GeneratedAnswersPayload,
)
from app.modules.generation.llm.v2.generators.distractor import (
    DistractorGenerator,
    GeneratedDistractorsPayload,
)
from app.modules.generation.llm.v2.generators.instruction_router import (
    InstructionRouterGenerator,
    RoutedUserInstructions,
)
from app.modules.generation.llm.v2.generators.question_stem import (
    GeneratedQuestionStemsPayload,
    QuestionStemGenerator,
)
from app.modules.generation.llm.v2.quiz_pipeline import FullQuizV2Pipeline

__all__ = [
    "ANSWER_GENERATOR_CHAIN_OF_THOUGHT",
    "ANSWER_GENERATOR_ROLE_DEFAULT",
    "AnswerGenerator",
    "GeneratedAnswersPayload",
    "DISTRACTOR_GENERATOR_CHAIN_OF_THOUGHT",
    "DISTRACTOR_GENERATOR_ROLE_DEFAULT",
    "INSTRUCTION_ROUTER_CHAIN_OF_THOUGHT",
    "INSTRUCTION_ROUTER_ROLE_DEFAULT",
    "InstructionRouterGenerator",
    "GeneratedDistractorsPayload",
    "DistractorGenerator",
    "RoutedUserInstructions",
    "FullQuizV2Pipeline",
    "GeneratedQuestionStemsPayload",
    "QUESTION_STEM_GENERATOR_ROLE_DEFAULT",
    "QuestionStemGenerator",
]
