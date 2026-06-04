from typing import Annotated

from fastapi import APIRouter, Depends, Request

from app.core.actions.initialize_workspace import (
    InitializeWorkspaceAction,
    WorkspaceContext,
)
from app.features.auth.models import AuthenticatedUser, LoginCredentials
from app.features.auth.session_service import SessionService
from app.server.dependencies.auth import get_current_user, get_session_service
from app.server.dependencies.workspace import get_initialize_workspace_action
from app.server.middleware.rate_limiting import limiter

router = APIRouter(prefix="/api")


@router.post("/workspace", response_model=WorkspaceContext)
@limiter.limit("10/minute")
async def initialize_workspace(
    request: Request,
    body: LoginCredentials,
    action: Annotated[
        InitializeWorkspaceAction, Depends(get_initialize_workspace_action)
    ],
    session_service: Annotated[SessionService, Depends(get_session_service)],
) -> WorkspaceContext:
    """Verifies user credentials and initializes the workspace context (course groups, tests)."""
    context = await action.execute(body)
    session_token = session_service.create_session(
        context.user_id,
        context.username,
    )
    return context.model_copy(update={"session_token": session_token})


@router.get("/workspace/me", response_model=WorkspaceContext)
async def get_workspace_me(
    user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    action: Annotated[
        InitializeWorkspaceAction, Depends(get_initialize_workspace_action)
    ],
) -> WorkspaceContext:
    """Return workspace context for the current session."""
    return await action.build_context(user)
