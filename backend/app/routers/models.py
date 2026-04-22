from typing import Any

from fastapi import APIRouter

from app.config import settings

router = APIRouter(prefix="/api")


@router.get("/models")
async def list_models() -> dict[str, list[Any]]:
    """Return available model list from AVAILABLE_MODELS env var. (BACK-03, D-03)"""
    return {"models": settings.available_models}
