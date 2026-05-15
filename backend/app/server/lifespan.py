import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings
from app.helpers.price_catalog import build_api_models_catalog


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    app.state.models_catalog = await asyncio.to_thread(
        build_api_models_catalog,
        settings,
    )
    yield
