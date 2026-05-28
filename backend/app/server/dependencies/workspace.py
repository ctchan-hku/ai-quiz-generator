from typing import Annotated

from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.actions.initialize_workspace import InitializeWorkspaceAction
from app.modules.auth.service import CredentialAuthService
from app.modules.auth.repository import UserRepository
from app.modules.data.course_groups.repository import CourseGroupRepository
from app.modules.data.course_groups.service import CourseGroupService
from app.modules.data.questions.repository import QuestionRepository
from app.modules.data.tests.repository import TestRepository
from app.server.dependencies.mongodb import get_database


def get_credential_auth_service(
    db: Annotated[AsyncIOMotorDatabase, Depends(get_database)],
) -> CredentialAuthService:
    return CredentialAuthService(UserRepository(db))


def get_initialize_workspace_action(
    db: Annotated[AsyncIOMotorDatabase, Depends(get_database)],
    auth_service: Annotated[
        CredentialAuthService, Depends(get_credential_auth_service)
    ],
) -> InitializeWorkspaceAction:
    return InitializeWorkspaceAction(
        auth_service,
        CourseGroupService(CourseGroupRepository(db)),
        TestRepository(db),
        QuestionRepository(db),
    )
