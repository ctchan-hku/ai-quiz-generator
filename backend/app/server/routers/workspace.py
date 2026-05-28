from typing import Annotated

from fastapi import APIRouter, Depends, Request

from app.core.actions.initialize_workspace import InitializeWorkspaceAction
from app.core.domain import WorkspaceContext
from app.modules.auth.models import LoginCredentials
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
) -> WorkspaceContext:
    """Verifies user credentials and initializes the workspace context (course groups, tests)."""
    return await action.execute(body)
