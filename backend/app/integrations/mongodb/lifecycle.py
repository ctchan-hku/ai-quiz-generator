from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient

from app.config import settings
from app.integrations.mongodb.client import create_motor_client
from app.integrations.mongodb.constants import MONGODB_DB_NAME


@asynccontextmanager
async def mongo_lifespan(app: FastAPI) -> AsyncIterator[None]:
    client: AsyncIOMotorClient | None = None
    if settings.mongodb_uri:
        client = create_motor_client(settings.mongodb_uri)
        app.state.mongodb_client = client
        app.state.mongodb_database = client[MONGODB_DB_NAME]
    else:
        app.state.mongodb_client = None
        app.state.mongodb_database = None
    yield
    if client is not None:
        client.close()
