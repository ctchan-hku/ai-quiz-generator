from typing import Annotated

from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.workflows.auth_workflow import AuthWorkflow
from app.modules.auth.handler import LoginHandler
from app.modules.auth.repository import UserRepository
from app.modules.data.course_groups.repository import CourseGroupRepository
from app.modules.data.course_groups.service import CourseGroupService
from app.modules.data.questions.repository import QuestionRepository
from app.modules.data.tests.repository import TestRepository
from app.server.dependencies.mongodb import get_database


def get_login_handler(
    db: Annotated[AsyncIOMotorDatabase, Depends(get_database)],
) -> LoginHandler:
    return LoginHandler(UserRepository(db))


def get_auth_workflow(
    db: Annotated[AsyncIOMotorDatabase, Depends(get_database)],
    login_handler: Annotated[LoginHandler, Depends(get_login_handler)],
) -> AuthWorkflow:
    return AuthWorkflow(
        login_handler,
        CourseGroupService(CourseGroupRepository(db)),
        TestRepository(db),
        QuestionRepository(db),
    )
