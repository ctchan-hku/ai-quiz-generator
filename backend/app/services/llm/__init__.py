"""LLM package: client/chat primitives, protocols, bases, full-quiz and single-MCQ workflows + parse helpers."""

from app.services.llm.bases import BaseChatGeneration, BaseLlmJsonParse
from app.services.llm.common import (
    CHAT_COMPLETION_KWARGS,
    MAX_COMPLETION_TOKENS,
    complete_chat,
    get_llm_client,
)
from app.services.llm.protocols import LLMGeneration, LlmJsonParse
from app.services.llm.question import SINGLE_MCQ_MAX_TOKENS, SingleMcqLlm
from app.services.llm.quiz import FullQuizLlm
from app.services.parser import (
    PARSE_RECOVERABLE,
    RETRY_LOG_PREFIX,
    LlmParseRetrySpec,
    load_llm_json_value,
    make_llm_parse_retry_spec,
    parse_llm_with_retry,
)

__all__ = [
    "CHAT_COMPLETION_KWARGS",
    "PARSE_RECOVERABLE",
    "RETRY_LOG_PREFIX",
    "BaseChatGeneration",
    "BaseLlmJsonParse",
    "LLMGeneration",
    "LlmJsonParse",
    "LlmParseRetrySpec",
    "make_llm_parse_retry_spec",
    "MAX_COMPLETION_TOKENS",
    "SINGLE_MCQ_MAX_TOKENS",
    "FullQuizLlm",
    "SingleMcqLlm",
    "complete_chat",
    "get_llm_client",
    "load_llm_json_value",
    "parse_llm_with_retry",
]
