from __future__ import annotations

from collections.abc import Callable
from typing import Any, Generic, TypeVar

from fastapi import HTTPException
from json_repair import repair_json
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage
from pydantic import BaseModel, ValidationError

from app.features.generation.helpers.logging import log_full_llm_chat
from app.features.generation.services.system_prompt_builder import SystemPromptBuilder
from app.integrations.langchain.config import MAX_COMPLETION_TOKENS
from app.integrations.langchain.token_usage import TokenUsage, TokenUsageCallbackHandler

T = TypeVar("T", bound=BaseModel)

PARSE_RECOVERABLE: tuple[type[Exception], ...] = (
    ValidationError,
    ValueError,
    TypeError,
)

PARSE_CORRECTIVE = (
    "That response was invalid JSON or failed schema validation. "
    "Follow the JSON shape required by the conversation above, with no extra text."
)

PARSE_RETRY_FAILURE_DETAIL = "LLM returned invalid data after retry"


def _message_text(message: BaseMessage | None) -> str:
    if message is None:
        return ""
    content = message.content
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict) and block.get("type") == "text":
                parts.append(str(block.get("text", "")))
        return "".join(parts)
    return str(content)


def _coerce_parsed(result: object, schema: type[T]) -> T:
    if isinstance(result, schema):
        return result
    if isinstance(result, dict):
        parsed = result.get("parsed")
        if isinstance(parsed, schema):
            return parsed
        parsing_error = result.get("parsing_error")
        if parsing_error is not None:
            raise parsing_error
    raise ValueError("Structured output did not return a parsed model")


def _parse_repaired_raw(
    raw_text: str,
    schema: type[T],
    finalize: Callable[[T], T] | None,
) -> T:
    repaired = repair_json(raw_text, return_objects=True)
    parsed = schema.model_validate(repaired)
    if finalize is not None:
        parsed = finalize(parsed)
    return parsed


def _log_success(
    *,
    label: str,
    chat_messages: list[dict[str, Any]],
    raw_text: str,
    model: str,
) -> None:
    log_full_llm_chat(
        label=label,
        messages=[*chat_messages, {"role": "assistant", "content": raw_text}],
        model=model,
    )


async def invoke_with_corrective_retry(
    llm: BaseChatModel,
    schema: type[T],
    messages: list[dict[str, Any]],
    *,
    max_tokens: int,
    step_name: str,
    model: str,
    finalize: Callable[[T], T] | None = None,
) -> tuple[T, TokenUsage]:
    usage = TokenUsage()
    structured = llm.with_structured_output(
        schema,
        method="json_mode",
        include_raw=True,
    ).bind(max_tokens=max_tokens)

    async def _single_invoke(
        chat_messages: list[dict[str, Any]],
        label: str,
    ) -> tuple[T | None, str, Exception | None]:
        callback = TokenUsageCallbackHandler()
        result = await structured.ainvoke(
            chat_messages,
            config={
                "callbacks": [callback],
                "run_name": label,
                "tags": [step_name, model],
            },
        )
        usage.__iadd__(callback.usage)
        raw_text = ""
        if isinstance(result, dict):
            raw_message = result.get("raw")
            raw_text = _message_text(
                raw_message if isinstance(raw_message, BaseMessage) else None,
            )
        try:
            parsed = _coerce_parsed(result, schema)
            if finalize is not None:
                parsed = finalize(parsed)
        except Exception as exc:
            if raw_text.strip() and isinstance(exc, PARSE_RECOVERABLE):
                try:
                    parsed = _parse_repaired_raw(raw_text, schema, finalize)
                except Exception:
                    return None, raw_text, exc
                else:
                    _log_success(
                        label=label,
                        chat_messages=chat_messages,
                        raw_text=raw_text,
                        model=model,
                    )
                    return parsed, raw_text, None
            return None, raw_text, exc
        _log_success(
            label=label,
            chat_messages=chat_messages,
            raw_text=raw_text,
            model=model,
        )
        return parsed, raw_text, None

    parsed, raw_text, error = await _single_invoke(messages, step_name)
    if error is None:
        return parsed, usage

    if not isinstance(error, PARSE_RECOVERABLE):
        raise error

    retry_messages = [
        *messages,
        {"role": "assistant", "content": raw_text},
        {"role": "user", "content": PARSE_CORRECTIVE},
    ]
    parsed, _, retry_error = await _single_invoke(
        retry_messages,
        f"{step_name} · retry",
    )
    if retry_error is None:
        return parsed, usage

    if not isinstance(retry_error, PARSE_RECOVERABLE):
        raise retry_error
    raise HTTPException(
        status_code=502,
        detail=PARSE_RETRY_FAILURE_DETAIL,
    ) from retry_error


class StructuredLlmStep(SystemPromptBuilder, Generic[T]):
    parse_response_model: type[T]

    def build_messages(self) -> list[dict[str, Any]]:
        raise NotImplementedError

    def post_process(self, parsed: T) -> T:
        return parsed

    @property
    def step_name(self) -> str:
        return type(self).__name__

    async def run(self, model: str, llm: BaseChatModel) -> tuple[T, TokenUsage]:
        messages = self.build_messages()
        parsed, usage = await invoke_with_corrective_retry(
            llm,
            self.parse_response_model,
            messages,
            max_tokens=MAX_COMPLETION_TOKENS,
            step_name=self.step_name,
            model=model,
            finalize=self.post_process,
        )
        return parsed, usage


__all__ = [
    "StructuredLlmStep",
    "invoke_with_corrective_retry",
]
