from datetime import datetime, timezone

from fastapi import APIRouter, Request

from app.config import settings
from app.integrations.mongodb.client import ping_mongo_server

router = APIRouter()


@router.get("/health")
async def health_check() -> dict:
    """Liveness endpoint. Must respond in < 50ms — no blocking I/O. (BACK-02)"""
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}


@router.get("/health/db")
async def database_health(request: Request) -> dict:
    """Readiness check for MongoDB; use the same URI in MongoDB Compass."""
    client = request.app.state.mongodb_client
    if client is None:
        return {
            "mongo": "disabled",
            "detail": "Set MONGODB_URI to enable MongoDB (same value as in Compass).",
        }
    await ping_mongo_server(client)
    return {
        "mongo": "ok",
        "database": settings.mongodb_db_name,
    }
