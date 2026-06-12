from fastapi import FastAPI
from openai import APIError
from slowapi.errors import RateLimitExceeded

from app.server.exception_handlers.mongo import register_mongo_exception_handlers
from app.server.exception_handlers.openai_upstream import openai_upstream_handler
from app.server.exception_handlers.rate_limit import rate_limit_handler


def register_exception_handlers(app: FastAPI) -> None:
    register_mongo_exception_handlers(app)
    app.add_exception_handler(RateLimitExceeded, rate_limit_handler)
    app.add_exception_handler(APIError, openai_upstream_handler)
