from datetime import datetime, timezone

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check() -> dict:
    """Liveness endpoint. Must respond in < 50ms — no blocking I/O. (BACK-02)"""
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}
