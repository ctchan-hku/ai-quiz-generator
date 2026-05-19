from typing import Any

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.modules.data.student_stats.models import TestRecord

TESTS_COLLECTION = "tests"
TEST_PROJECTION = {
    "_id": 1,
    "name": 1,
    "questions": 1,
    "grade_cutoff": 1,
}


class TestRepository:
    __test__ = False

    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self._collection = db[TESTS_COLLECTION]

    async def find_by_course_group_id(self, course_group_id: str) -> list[TestRecord]:
        cursor = self._collection.find(
            self._course_group_query(course_group_id),
            TEST_PROJECTION,
        )
        documents = await cursor.to_list(length=None)
        return [
            self._to_test_record(document)
            for document in documents
            if "name" in document
        ]

    @staticmethod
    def _course_group_query(course_group_id: str) -> dict[str, Any]:
        field = "course_group_details.id"
        if ObjectId.is_valid(course_group_id):
            object_id = ObjectId(course_group_id)
            return {field: {"$in": [course_group_id, object_id]}}
        return {field: course_group_id}

    @staticmethod
    def _to_test_record(document: dict[str, Any]) -> TestRecord:
        return TestRecord(
            id=str(document["_id"]),
            name=document["name"],
            questions=document.get("questions", []),
            grade_cutoff=document.get("grade_cutoff", []),
        )
