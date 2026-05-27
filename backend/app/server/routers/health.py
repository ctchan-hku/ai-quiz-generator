from datetime import datetime, timezone

from fastapi import APIRouter, Request
from pydantic import BaseModel

from app.integrations.mongodb.client import ping_mongo_server

router = APIRouter()


class HealthResponse(BaseModel):
    status: str
    timestamp: str


def health_payload(status: str) -> HealthResponse:
    return HealthResponse(
        status=status,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Liveness endpoint. Must respond in < 50ms — no blocking I/O. (BACK-02)"""
    return health_payload("ok")


@router.get("/db/health", response_model=HealthResponse, tags=["database"])
async def database_health(request: Request) -> HealthResponse:
    """Readiness check for the database; use the same URI in MongoDB Compass."""
    client = request.app.state.mongodb_client
    if client is None:
        return health_payload("disabled")
    await ping_mongo_server(client)
    return health_payload("ok")
