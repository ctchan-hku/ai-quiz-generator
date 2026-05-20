from typing import Any

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.modules.data.student_stats.models import QuestionRecord, ResponseNrl

QUESTIONS_COLLECTION = "questions"
QUESTION_PROJECTION = {
    "_id": 1,
    "prompt": 1,
    "interface": 1,
    "response_nrl": 1,
}


class QuestionRepository:
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self._collection = db[QUESTIONS_COLLECTION]

    async def find_by_ids_in_order(
        self,
        question_refs: list[Any],
        *,
        types: tuple[str, ...] | None = None,
    ) -> list[QuestionRecord]:
        question_ids = [_question_ref_to_id(ref) for ref in question_refs]
        if not question_ids:
            return []

        query: dict[str, Any] = {"_id": {"$in": _query_ids(question_ids)}}
        if types is not None:
            query["interface.name"] = {"$in": list(types)}

        cursor = self._collection.find(query, QUESTION_PROJECTION)
        documents = await cursor.to_list(length=None)
        by_id = {
            str(document["_id"]): _to_question_record(document)
            for document in documents
        }
        return [
            by_id[question_id] for question_id in question_ids if question_id in by_id
        ]


def _question_ref_to_id(ref: Any) -> str:
    raw_id = ref["_id"] if isinstance(ref, dict) else ref
    return str(raw_id)


def _query_ids(question_ids: list[str]) -> list[Any]:
    values: list[Any] = []
    for question_id in question_ids:
        values.append(question_id)
        if ObjectId.is_valid(question_id):
            values.append(ObjectId(question_id))
    return values


def _to_question_record(document: dict[str, Any]) -> QuestionRecord:
    response_nrl = document["response_nrl"]
    return QuestionRecord(
        id=str(document["_id"]),
        prompt=document["prompt"],
        type=str(document["interface"]["name"]),
        response_nrl=ResponseNrl(specification=response_nrl["specification"]),
    )
