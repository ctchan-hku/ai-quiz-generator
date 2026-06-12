from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pymongo.errors import AutoReconnect, ConnectionFailure, ServerSelectionTimeoutError

_MONGO_ERRORS = (
    AutoReconnect,
    ConnectionFailure,
    ServerSelectionTimeoutError,
)
_UNAVAILABLE = "Database temporarily unavailable"


def register_mongo_exception_handlers(app: FastAPI) -> None:
    async def mongo_unavailable_handler(
        _request: Request,
        _exc: Exception,
    ) -> JSONResponse:
        return JSONResponse(status_code=503, content={"detail": _UNAVAILABLE})

    for exc_type in _MONGO_ERRORS:
        app.add_exception_handler(exc_type, mongo_unavailable_handler)
