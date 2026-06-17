import asyncio
import contextlib
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.features.workspace.core.index_store import FaissIndexStore
from app.features.workspace.course_tests.build_index import build_course_tests_index
from app.features.workspace.course_tests.constants import COURSE_TESTS_INDEX_DIR
from app.integrations.mongodb.lifecycle import mongo_lifespan
from app.server.constants import ALLOWED_ORIGINS
from app.server.exception_handlers import register_exception_handlers
from app.server.middleware.rate_limiting import limiter
from app.server.routers import register_routers

logger = logging.getLogger(__name__)


async def _load_course_tests_vector_store() -> object | None:
    store = FaissIndexStore(COURSE_TESTS_INDEX_DIR)
    if store.exists():
        return await asyncio.to_thread(store.load)

    if not settings.mongodb_connection_string:
        return None

    logger.info(
        "Course-tests index missing at %s; building from MongoDB",
        COURSE_TESTS_INDEX_DIR,
    )
    try:
        await build_course_tests_index()
    except Exception:
        logger.exception("Failed to build course-tests index on startup")
        return None

    if store.exists():
        return await asyncio.to_thread(store.load)
    return None


@asynccontextmanager
async def _app_lifespan(app: FastAPI) -> AsyncIterator[None]:
    async with mongo_lifespan(app):
        app.state.vector_store = None

        async def load_vector_store() -> None:
            app.state.vector_store = await _load_course_tests_vector_store()

        load_task = asyncio.create_task(load_vector_store())
        try:
            yield
        finally:
            load_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await load_task


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
        allow_origins=ALLOWED_ORIGINS,
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    register_routers(app)
    return app
