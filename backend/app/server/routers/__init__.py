import logging

from fastapi import FastAPI

from app.config import settings
from app.server.routers import courses, db, generate, health, models

logger = logging.getLogger(__name__)


def register_routers(app: FastAPI) -> None:
    app.include_router(health.router)
    app.include_router(db.router)
    app.include_router(models.router)
    app.include_router(courses.router)
    app.include_router(generate.router)
    if settings.enable_debug_chat_completion:
        from app.server.routers import debug

        app.include_router(debug.router)
        logger.warning(
            "Debug chat-completion route is ENABLED. "
            "Disable ENABLE_DEBUG_CHAT_COMPLETION before production deployment.",
        )
