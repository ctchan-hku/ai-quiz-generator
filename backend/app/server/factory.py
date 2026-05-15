from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.server.exception_handlers import register_exception_handlers
from app.server.lifespan import lifespan
from app.server.middleware.rate_limiting import limiter
from app.server.routers import register_routers


def create_app() -> FastAPI:
    app = FastAPI(title="AI Quiz Generator", version="0.1.0", lifespan=lifespan)
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
