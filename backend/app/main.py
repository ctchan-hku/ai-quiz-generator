import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.limiter import limiter
from app.routers import generate, health, models

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Quiz Generator", version="0.1.0")
app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    return JSONResponse(
        status_code=429,
        content={"detail": "You've hit the limit of 3 quizzes per hour. Please wait before trying again."},
    )

# CORSMiddleware MUST be added before include_router calls (BACK-01, D-06).
# Phase 1: ALLOWED_ORIGINS=* for dev convenience.
# Phase 3: tighten to Vercel URL + http://localhost:5173 (D-07).
# CRITICAL: allow_credentials=False is required when allow_origins=["*"].
#           FastAPI raises RuntimeError if allow_credentials=True with wildcard origin.
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

# Conditional debug router (D-08). When false, the route is not registered (OpenAPI and 404 both omit it).
# WARNING: Keep ENABLE_DEBUG_CHAT_COMPLETION=false on production (D-10).
if settings.enable_debug_chat_completion:
    from app.routers import debug  # local import — only when gate is true

    app.include_router(debug.router)
    logger.warning(
        "Debug chat-completion route is ENABLED. "
        "Disable ENABLE_DEBUG_CHAT_COMPLETION before production deployment.",
    )
