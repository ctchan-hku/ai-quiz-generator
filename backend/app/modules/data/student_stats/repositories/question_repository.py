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
    ) -> list[QuestionRecord]:
        question_ids = [_question_ref_to_id(ref) for ref in question_refs]
        question_ids = [question_id for question_id in question_ids if question_id]
        if not question_ids:
            return []

        cursor = self._collection.find(
            {"_id": {"$in": _query_ids(question_ids)}},
            QUESTION_PROJECTION,
        )
        documents = await cursor.to_list(length=None)
        by_id = {
            str(document["_id"]): _to_question_record(document)
            for document in documents
        }

        ordered: list[QuestionRecord] = []
        for question_id in question_ids:
            record = by_id.get(question_id)
            if record is not None:
                ordered.append(record)
        return ordered


def _question_ref_to_id(ref: Any) -> str | None:
    if isinstance(ref, dict):
        raw_id = ref.get("_id") or ref.get("id")
    else:
        raw_id = ref
    if raw_id is None:
        return None
    return str(raw_id)


def _query_ids(question_ids: list[str]) -> list[Any]:
    values: list[Any] = []
    seen: set[str] = set()
    for question_id in question_ids:
        if question_id in seen:
            continue
        seen.add(question_id)
        values.append(question_id)
        if ObjectId.is_valid(question_id):
            values.append(ObjectId(question_id))
    return values


def _to_question_record(document: dict[str, Any]) -> QuestionRecord:
    return QuestionRecord(
        id=str(document["_id"]),
        prompt=document.get("prompt"),
        type=_to_question_type(document.get("interface")),
        response_nrl=_to_response_nrl(document.get("response_nrl")),
    )


def _to_question_type(interface_raw: Any) -> str | None:
    if not isinstance(interface_raw, dict):
        return None
    name = interface_raw.get("name")
    if name is None:
        return None
    return str(name)


def _to_response_nrl(raw: Any) -> ResponseNrl | None:
    if not isinstance(raw, dict):
        return None
    return ResponseNrl(specification=raw.get("specification"))
