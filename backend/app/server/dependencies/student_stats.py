from typing import Annotated

from fastapi import Depends, Request
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.workflows.student_stats_workflow import StudentStatsWorkflow
from app.modules.data.course_groups.repository import CourseGroupRepository
from app.modules.data.course_groups.service import CourseGroupService
from app.modules.data.questions.repository import QuestionRepository
from app.modules.data.responses.repository import ResponseRepository
from app.modules.data.responses.service import ResponseService
from app.modules.data.tests.repository import TestRepository
from app.modules.data.tests.service import TestService
from app.modules.student_stats.service import QuestionMetricsService
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


def _build_student_stats_workflow(db: AsyncIOMotorDatabase) -> StudentStatsWorkflow:
    return StudentStatsWorkflow(
        TestRepository(db),
        QuestionRepository(db),
        ResponseRepository(db),
        QuestionMetricsService(),
    )


def get_student_stats_workflow(
    db: Annotated[AsyncIOMotorDatabase, Depends(get_database)],
) -> StudentStatsWorkflow:
    return _build_student_stats_workflow(db)


def get_optional_student_stats_workflow(
    request: Request,
) -> StudentStatsWorkflow | None:
    db = request.app.state.mongodb_database
    if db is None:
        return None
    return _build_student_stats_workflow(db)
