from typing import Any

from fastapi import APIRouter

from app.config import settings

router = APIRouter(prefix="/api")


@router.get("/models")
async def list_models() -> dict[str, list[Any]]:
    """Objects from the AVAILABLE_MODELS JSON array (as stored in config)."""
    return {"models": list(settings.available_models)}
