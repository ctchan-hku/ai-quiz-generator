from typing import Annotated

from fastapi import Depends, Request
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.actions.derive_question_metrics import DeriveQuestionMetricsAction
from app.domains.course_groups.repository import CourseGroupRepository
from app.domains.course_groups.service import CourseGroupService
from app.domains.questions.repository import QuestionRepository
from app.domains.responses.repository import ResponseRepository
from app.domains.responses.service import ResponseService
from app.domains.tests.repository import TestRepository
from app.domains.tests.service import TestService
from app.modules.item_analysis.service import ItemAnalysisService
from app.server.dependencies.mongodb import get_database


def get_course_group_service(
    db: Annotated[AsyncIOMotorDatabase, Depends(get_database)],
) -> CourseGroupService:
    return CourseGroupService(CourseGroupRepository(db))


def get_test_service(request: Request) -> TestService:
    db = request.app.state.mongodb_database
    repository = TestRepository(db) if db is not None else None
    return TestService(repository)


def get_response_service(
    db: Annotated[AsyncIOMotorDatabase, Depends(get_database)],
) -> ResponseService:
    return ResponseService(ResponseRepository(db))


def _build_item_analysis_action(
    db: AsyncIOMotorDatabase,
) -> DeriveQuestionMetricsAction:
    return DeriveQuestionMetricsAction(
        TestRepository(db),
        QuestionRepository(db),
        ResponseRepository(db),
        ItemAnalysisService(),
    )


def get_item_analysis_action(
    db: Annotated[AsyncIOMotorDatabase, Depends(get_database)],
) -> DeriveQuestionMetricsAction:
    return _build_item_analysis_action(db)


def get_optional_item_analysis_action(
    request: Request,
) -> DeriveQuestionMetricsAction | None:
    db = request.app.state.mongodb_database
    if db is None:
        return None
    return _build_item_analysis_action(db)
