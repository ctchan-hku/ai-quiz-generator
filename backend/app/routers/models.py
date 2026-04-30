from typing import Any

from fastapi import APIRouter, Request

from app.config import settings

router = APIRouter(prefix="/api")


@router.get("/models")
async def list_models(request: Request) -> dict[str, list[Any]]:
    """AVAILABLE_MODELS ids + labels; prices from backend/data/poe_ai_models.json when id matches."""
    catalog = getattr(request.app.state, "models_catalog", None)
    if catalog is None:
        catalog = settings.available_models
    return {"models": catalog}
