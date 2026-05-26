from typing import Annotated

from fastapi import APIRouter, Depends, Request

from app.modules.data.auth.models import LoginRequest, LoginResponse
from app.modules.data.auth.services.login_service import LoginService
from app.server.dependencies.auth import get_login_service
from app.server.middleware.rate_limiting import limiter

router = APIRouter(prefix="/api")


@router.post("/login", response_model=LoginResponse)
@limiter.limit("10/minute")
async def login(
    request: Request,
    body: LoginRequest,
    service: Annotated[LoginService, Depends(get_login_service)],
) -> LoginResponse:
    return await service.login(body)
