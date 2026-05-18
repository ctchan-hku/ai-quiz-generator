from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient

from app.config import settings
from app.integrations.mongodb.client import create_motor_client


@asynccontextmanager
async def mongo_lifespan(app: FastAPI) -> AsyncIterator[None]:
    client: AsyncIOMotorClient | None = None
    if settings.mongodb_uri:
        client = create_motor_client(settings.mongodb_uri)
        app.state.mongodb_client = client
        app.state.mongodb_database = client[settings.mongodb_db_name]
    else:
        app.state.mongodb_client = None
        app.state.mongodb_database = None
    yield
    if client is not None:
        client.close()
