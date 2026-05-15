from fastapi import Request
from fastapi.responses import JSONResponse
from openai import APIError

from app.helpers.openai_upstream_error import log_upstream_openai_api_error


async def openai_upstream_handler(
    _request: Request,
    exc: APIError,
) -> JSONResponse:
    log_upstream_openai_api_error(exc)
    return JSONResponse(
        status_code=502,
        content={"detail": "Upstream language model request failed."},
    )
