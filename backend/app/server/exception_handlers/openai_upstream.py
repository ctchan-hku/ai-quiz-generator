from __future__ import annotations

import json
import logging
from typing import Any

from fastapi import Request
from fastapi.responses import JSONResponse
from openai import APIError, APIStatusError

logger = logging.getLogger(__name__)


def _build_upstream_log_payload(exc: APIError) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "exception_type": type(exc).__name__,
        "message": exc.message,
    }
    if exc.code is not None:
        payload["code"] = exc.code
    if exc.param is not None:
        payload["param"] = exc.param
    if exc.type is not None:
        payload["type"] = exc.type
    if isinstance(exc, APIStatusError):
        payload["status_code"] = exc.status_code
        if exc.request_id:
            payload["request_id"] = exc.request_id
        payload["response_body"] = exc.body
    payload["request_method"] = exc.request.method
    payload["request_url"] = str(exc.request.url)
    return payload


def _log_upstream_error(exc: APIError) -> None:
    payload = _build_upstream_log_payload(exc)
    logger.error(
        "Upstream OpenAI-compatible API failure: %s",
        json.dumps(payload, ensure_ascii=False, default=str),
        exc_info=True,
    )


async def openai_upstream_handler(
    _request: Request,
    exc: APIError,
) -> JSONResponse:
    _log_upstream_error(exc)
    return JSONResponse(
        status_code=502,
        content={"detail": "Upstream language model request failed."},
    )
