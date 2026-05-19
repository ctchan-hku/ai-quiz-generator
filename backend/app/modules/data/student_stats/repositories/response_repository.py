from typing import Any

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.modules.data.student_stats.models import ResponseRecord

RESPONSES_COLLECTION = "responses"
TEMPLATE_TYPE_TEST = "test"
RESPONSE_PROJECTION = {
    "_id": 1,
    "answer": 1,
}


class ResponseRepository:
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self._collection = db[RESPONSES_COLLECTION]

    async def find_by_test_id(self, test_id: str) -> list[ResponseRecord]:
        cursor = self._collection.find(
            self._test_template_query(test_id),
            RESPONSE_PROJECTION,
        )
        documents = await cursor.to_list(length=None)
        return [self._to_response_record(document) for document in documents]

    @staticmethod
    def _test_template_query(test_id: str) -> dict[str, Any]:
        template_id_field = "template.id"
        if ObjectId.is_valid(test_id):
            object_id = ObjectId(test_id)
            return {
                template_id_field: {"$in": [test_id, object_id]},
                "template.type": TEMPLATE_TYPE_TEST,
            }
        return {
            template_id_field: test_id,
            "template.type": TEMPLATE_TYPE_TEST,
        }

    @staticmethod
    def _to_response_record(document: dict[str, Any]) -> ResponseRecord:
        return ResponseRecord(
            id=str(document["_id"]),
            answers=document.get("answer", []),
        )
