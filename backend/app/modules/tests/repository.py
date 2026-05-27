from typing import Any

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.modules.tests.models import TestRecord

TESTS_COLLECTION = "tests"
TEST_PROJECTION = {
    "_id": 1,
    "name": 1,
    "questions": 1,
    "grade_cutoff": 1,
}


def _query_ids(test_ids: list[str]) -> list[Any]:
    values: list[Any] = []
    for test_id in test_ids:
        values.append(test_id)
        if ObjectId.is_valid(test_id):
            values.append(ObjectId(test_id))
    return values


class TestRepository:
    __test__ = False

    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self._collection = db[TESTS_COLLECTION]

    async def find_by_id(self, test_id: str) -> TestRecord | None:
        document = await self._collection.find_one(
            self._id_query(test_id),
            TEST_PROJECTION,
        )
        if document is None:
            return None
        return self._to_test_record(document)

    async def find_by_ids(self, test_ids: list[str]) -> list[TestRecord]:
        if not test_ids:
            return []
        cursor = self._collection.find(
            {"_id": {"$in": _query_ids(test_ids)}},
            TEST_PROJECTION,
        )
        documents = await cursor.to_list(length=None)
        by_id = {
            str(document["_id"]): self._to_test_record(document)
            for document in documents
        }
        return [by_id[test_id] for test_id in test_ids if test_id in by_id]

    async def find_by_course_group_id(self, course_group_id: str) -> list[TestRecord]:
        cursor = self._collection.find(
            self._course_group_query(course_group_id),
            TEST_PROJECTION,
        )
        documents = await cursor.to_list(length=None)
        return [self._to_test_record(document) for document in documents]

    @staticmethod
    def _id_query(test_id: str) -> dict[str, Any]:
        if ObjectId.is_valid(test_id):
            object_id = ObjectId(test_id)
            return {"_id": {"$in": [test_id, object_id]}}
        return {"_id": test_id}

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
            questions=document["questions"],
            grade_cutoff=document["grade_cutoff"],
        )
