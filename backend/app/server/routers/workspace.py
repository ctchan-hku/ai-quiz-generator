from typing import Annotated

from fastapi import APIRouter, Depends, Request

from app.core.actions.initialize_workspace import InitializeWorkspaceAction
from app.modules.workspace_auth.models import WorkspaceContext, WorkspaceCredentials
from app.server.dependencies.workspace import get_initialize_workspace_action
from app.server.middleware.rate_limiting import limiter

router = APIRouter(prefix="/api")


@router.post("/login", response_model=WorkspaceContext)
@limiter.limit("10/minute")
async def login(
    request: Request,
    body: WorkspaceCredentials,
    action: Annotated[
        InitializeWorkspaceAction, Depends(get_initialize_workspace_action)
    ],
) -> WorkspaceContext:
    """Verifies user credentials and initializes the workspace context (course groups, tests)."""
    return await action.execute(body)
