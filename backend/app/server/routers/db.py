from fastapi import APIRouter, Request

from app.config import settings
from app.integrations.mongodb.client import ping_mongo_server
from app.integrations.mongodb.health import HealthResponse

router = APIRouter(prefix="/db", tags=["database"])


@router.get("/health", response_model=HealthResponse)
async def database_health(request: Request) -> HealthResponse:
    """Readiness check for the database; use the same URI in MongoDB Compass."""
    client = request.app.state.mongodb_client
    if client is None:
        return HealthResponse(
            status="disabled",
            detail="Set MONGODB_URI to enable MongoDB (same value as in Compass).",
        )
    await ping_mongo_server(client)
    return HealthResponse(
        status="ok",
        database=settings.mongodb_db_name,
    )
