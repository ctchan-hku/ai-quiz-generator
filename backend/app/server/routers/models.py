from typing import Any

from fastapi import APIRouter

from app.config import settings

router = APIRouter(prefix="/api")


@router.get("/models")
async def list_models() -> dict[str, list[Any]]:
    return {"models": list(settings.available_models)}
