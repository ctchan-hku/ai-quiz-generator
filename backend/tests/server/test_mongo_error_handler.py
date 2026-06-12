import pytest
from httpx import ASGITransport, AsyncClient
from fastapi import FastAPI
from pymongo.errors import AutoReconnect

from app.server.exception_handlers.mongo import register_mongo_exception_handlers


@pytest.mark.asyncio
async def test_mongo_auto_reconnect_returns_503() -> None:
    app = FastAPI()
    register_mongo_exception_handlers(app)

    @app.get("/boom")
    async def boom() -> None:
        raise AutoReconnect("gi20db:27017: connection refused")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/boom")

    assert response.status_code == 503
    assert response.json()["detail"] == "Database temporarily unavailable"
