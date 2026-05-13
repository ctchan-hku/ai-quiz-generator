import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.helpers.price_catalog import build_api_models_catalog
from app.limiter import limiter
from app.routers import generate, health, models

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.models_catalog = await asyncio.to_thread(
        build_api_models_catalog, settings
    )
    yield


app = FastAPI(title="AI Quiz Generator", version="0.1.0", lifespan=lifespan)
app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    return JSONResponse(
        status_code=429,
        content={
            "detail": "You've hit the limit of 3 quizzes per hour. Please wait before trying again."
        },
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(models.router)
app.include_router(generate.router)

if settings.enable_debug_chat_completion:
    from app.routers import debug

    app.include_router(debug.router)
    logger.warning(
        "Debug chat-completion route is ENABLED. "
        "Disable ENABLE_DEBUG_CHAT_COMPLETION before production deployment.",
    )
