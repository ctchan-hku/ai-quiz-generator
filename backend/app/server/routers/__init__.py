import logging

from fastapi import FastAPI

from app.config import settings
from app.server.routers import auth, course_groups, health, models, tests, upload
from app.server.routers.question_edit import router as question_edit_router
from app.server.routers.test_generation import router as test_generation_router

logger = logging.getLogger(__name__)


def register_routers(app: FastAPI) -> None:
    app.include_router(health.router)
    app.include_router(models.router)
    app.include_router(auth.router)
    app.include_router(course_groups.router)
    app.include_router(tests.router)
    app.include_router(upload.router)
    app.include_router(test_generation_router)
    app.include_router(question_edit_router)
    if settings.enable_debug_chat_completion:
        from app.server.routers import llm_smoke_test

        app.include_router(llm_smoke_test.router)
        logger.warning(
            "Debug chat-completion route is ENABLED. "
            "Disable ENABLE_DEBUG_CHAT_COMPLETION before production deployment.",
        )
