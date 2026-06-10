from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.actions.initialize_workspace import (
    InitializeWorkspaceAction,
    WorkspaceContext,
)
from app.features.auth.models import AuthenticatedUser
from app.server.dependencies.auth import get_current_user
from app.server.dependencies.workspace import get_initialize_workspace_action

router = APIRouter(prefix="/api")


@router.get("/workspace/me", response_model=WorkspaceContext)
async def get_workspace_me(
    user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    action: Annotated[
        InitializeWorkspaceAction, Depends(get_initialize_workspace_action)
    ],
) -> WorkspaceContext:
    return await action.build_context(user)
