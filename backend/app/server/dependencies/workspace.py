from typing import Annotated

from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.actions.initialize_workspace import InitializeWorkspaceAction
from app.domains.course_groups.repository import CourseGroupRepository
from app.domains.course_groups.service import CourseGroupService
from app.domains.questions.repository import QuestionRepository
from app.domains.tests.repository import TestRepository
from app.server.dependencies.mongodb import get_database


def get_initialize_workspace_action(
    db: Annotated[AsyncIOMotorDatabase, Depends(get_database)],
) -> InitializeWorkspaceAction:
    return InitializeWorkspaceAction(
        CourseGroupService(CourseGroupRepository(db)),
        TestRepository(db),
        QuestionRepository(db),
    )
