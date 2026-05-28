from typing import Annotated

from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.actions.initialize_workspace import InitializeWorkspaceAction
from app.modules.data.course_groups.repository import CourseGroupRepository
from app.modules.data.course_groups.service import CourseGroupService
from app.modules.data.questions.repository import QuestionRepository
from app.modules.data.tests.repository import TestRepository
from app.modules.workspace_auth.authenticator import CredentialAuthenticator
from app.modules.workspace_auth.repository import UserRepository
from app.server.dependencies.mongodb import get_database


def get_credential_authenticator(
    db: Annotated[AsyncIOMotorDatabase, Depends(get_database)],
) -> CredentialAuthenticator:
    return CredentialAuthenticator(UserRepository(db))


def get_initialize_workspace_action(
    db: Annotated[AsyncIOMotorDatabase, Depends(get_database)],
    authenticator: Annotated[
        CredentialAuthenticator, Depends(get_credential_authenticator)
    ],
) -> InitializeWorkspaceAction:
    return InitializeWorkspaceAction(
        authenticator,
        CourseGroupService(CourseGroupRepository(db)),
        TestRepository(db),
        QuestionRepository(db),
    )
