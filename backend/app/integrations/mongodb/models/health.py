from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Readiness payload for the configured database connection."""

    status: str
    database: str | None = None
    detail: str | None = None
