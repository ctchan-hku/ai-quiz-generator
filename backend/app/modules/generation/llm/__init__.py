"""Generation LLM task implementations (single MCQ, question generator, answer deriver, distractor generator)."""

from app.modules.generation.llm.answer_deriver import (
    ANSWER_DERIVER_CHAIN_OF_THOUGHT,
    ANSWER_DERIVER_ROLE_DEFAULT,
    AnswerDeriverLlm,
    AnswerWithExplanation,
    DerivedAnswersPayload,
)
from app.modules.generation.llm.distractor_generator import (
    DISTRACTOR_GENERATOR_CHAIN_OF_THOUGHT,
    DISTRACTOR_GENERATOR_ROLE_DEFAULT,
    DerivedDistractorsPayload,
    DistractorGeneratorLlm,
    DistractorSet,
)
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
    "DISTRACTOR_GENERATOR_CHAIN_OF_THOUGHT",
    "DISTRACTOR_GENERATOR_ROLE_DEFAULT",
    "DerivedDistractorsPayload",
    "DistractorGeneratorLlm",
    "DistractorSet",
    "GeneratedQuestionsPayload",
    "QUESTION_GENERATOR_ROLE_DEFAULT",
    "QuestionGeneratorLlm",
    "SINGLE_MCQ_MAX_TOKENS",
    "SingleMcqLlm",
]
