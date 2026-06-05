from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.features.workspace.course_tests.index_store import index_exists, load_index
from app.integrations.mongodb.lifecycle import mongo_lifespan
from app.server.exception_handlers import register_exception_handlers
from app.server.middleware.rate_limiting import limiter
from app.server.routers import register_routers


@asynccontextmanager
async def _app_lifespan(app: FastAPI) -> AsyncIterator[None]:
    async with mongo_lifespan(app):
        if index_exists():
            app.state.similarity_vector_store = load_index()
        else:
            app.state.similarity_vector_store = None
        yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="AI Test Generator",
        version="0.1.0",
        lifespan=_app_lifespan,
    )
    app.state.limiter = limiter
    register_exception_handlers(app)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    register_routers(app)
    return app
