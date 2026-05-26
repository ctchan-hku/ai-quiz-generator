from typing import Annotated

from fastapi import APIRouter, Depends, Request

from app.modules.data.auth.handlers.login_handler import LoginHandler
from app.modules.data.auth.models import LoginRequest, LoginResponse
from app.server.dependencies.auth import get_login_handler
from app.server.middleware.rate_limiting import limiter

router = APIRouter(prefix="/api")


@router.post("/login", response_model=LoginResponse)
@limiter.limit("10/minute")
async def login(
    request: Request,
    body: LoginRequest,
    handler: Annotated[LoginHandler, Depends(get_login_handler)],
) -> LoginResponse:
    return await handler.login(body)
