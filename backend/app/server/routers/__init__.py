import logging

from fastapi import FastAPI

from app.config import settings
from app.modules.course_groups.router import router as course_groups_router
from app.modules.generation.router import router as generate_router
from app.modules.tests.router import router as tests_router
from app.server.routers import auth, db, health, models, upload

logger = logging.getLogger(__name__)


def register_routers(app: FastAPI) -> None:
    app.include_router(health.router)
    app.include_router(db.router)
    app.include_router(models.router)
    app.include_router(auth.router)
    app.include_router(course_groups_router)
    app.include_router(tests_router)
    app.include_router(upload.router)
    app.include_router(generate_router)
    if settings.enable_debug_chat_completion:
        from app.server.routers import debug

        app.include_router(debug.router)
        logger.warning(
            "Debug chat-completion route is ENABLED. "
            "Disable ENABLE_DEBUG_CHAT_COMPLETION before production deployment.",
        )
