from typing import Annotated

from fastapi import APIRouter, Depends, Request

from app.core.workflows.auth_workflow import AuthWorkflow, LoginResponse
from app.modules.auth.models import LoginRequest
from app.server.dependencies.auth import get_auth_workflow
from app.server.middleware.rate_limiting import limiter

router = APIRouter(prefix="/api")


@router.post("/login", response_model=LoginResponse)
@limiter.limit("10/minute")
async def login(
    request: Request,
    body: LoginRequest,
    workflow: Annotated[AuthWorkflow, Depends(get_auth_workflow)],
) -> LoginResponse:
    return await workflow.login_and_enrich(body)
