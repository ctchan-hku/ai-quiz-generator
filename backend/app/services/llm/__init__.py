"""LLM package: client/chat primitives, protocols, bases, full-quiz and single-MCQ workflows + parse helpers."""

from app.modules.generation.services.parser import (
    PARSE_RECOVERABLE,
    RETRY_LOG_PREFIX,
    BaseLlmJsonParse,
    PARSE_RETRY_FAILURE_DETAIL,
    parse_llm_with_retry,
    strip_fences,
)
from app.services.llm.core.bases import BaseChatGeneration
from app.services.llm.core.protocols import LLMGeneration, LlmJsonParse
from app.services.llm.full_quiz import FullQuizLlm
from app.services.llm.openai.client import (
    CHAT_COMPLETION_KWARGS,
    MAX_COMPLETION_TOKENS,
    complete_chat,
    get_llm_client,
)
from app.services.llm.single_mcq import SINGLE_MCQ_MAX_TOKENS, SingleMcqLlm

__all__ = [
    "CHAT_COMPLETION_KWARGS",
    "PARSE_RECOVERABLE",
    "PARSE_RETRY_FAILURE_DETAIL",
    "RETRY_LOG_PREFIX",
    "BaseChatGeneration",
    "BaseLlmJsonParse",
    "LLMGeneration",
    "LlmJsonParse",
    "MAX_COMPLETION_TOKENS",
    "SINGLE_MCQ_MAX_TOKENS",
    "FullQuizLlm",
    "SingleMcqLlm",
    "complete_chat",
    "get_llm_client",
    "parse_llm_with_retry",
    "strip_fences",
]
