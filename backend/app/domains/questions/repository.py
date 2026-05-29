from typing import Any

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.domains.questions.constants import DISTRIBUTABLE_QUESTION_TYPES
from app.domains.questions.models import QuestionRecord, ResponseNrl

QUESTIONS_COLLECTION = "questions"
QUESTION_PROJECTION = {
    "_id": 1,
    "prompt": 1,
    "interface": 1,
    "response_nrl": 1,
}


def _prompt_key_stages() -> list[dict[str, Any]]:
    return [
        {
            "$match": {
                "interface.name": {"$in": list(DISTRIBUTABLE_QUESTION_TYPES)},
                "prompt": {"$type": "string"},
            }
        },
        {"$addFields": {"_prompt_key": {"$trim": {"input": "$prompt"}}}},
        {"$match": {"_prompt_key": {"$ne": ""}}},
    ]


class QuestionRepository:
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self._collection = db[QUESTIONS_COLLECTION]

    async def find_by_ids_in_order(
        self,
        question_refs: list[Any],
    ) -> list[QuestionRecord]:
        question_ids = [_question_ref_to_id(ref) for ref in question_refs]
        if not question_ids:
            return []

        query: dict[str, Any] = {
            "_id": {"$in": _query_ids(question_ids)},
            "interface.name": {"$in": list(DISTRIBUTABLE_QUESTION_TYPES)},
        }

        cursor = self._collection.find(query, QUESTION_PROJECTION)
        documents = await cursor.to_list(length=None)
        by_id = {
            str(document["_id"]): _to_question_record(document)
            for document in documents
        }
        return [
            by_id[question_id] for question_id in question_ids if question_id in by_id
        ]

    async def stream_all_unique(self) -> tuple[list[QuestionRecord], int]:
        """Return one record per trimmed prompt and the pre-dedup row count."""
        pipeline = [
            *_prompt_key_stages(),
            {
                "$facet": {
                    "stats": [{"$count": "total"}],
                    "unique": [
                        {"$sort": {"_id": 1}},
                        {
                            "$group": {
                                "_id": "$_prompt_key",
                                "doc": {"$first": "$$ROOT"},
                            }
                        },
                        {"$replaceRoot": {"newRoot": "$doc"}},
                        {"$project": QUESTION_PROJECTION},
                    ],
                }
            },
        ]
        results = await self._collection.aggregate(pipeline).to_list(length=1)
        if not results:
            return [], 0

        facet = results[0]
        stats = facet["stats"]
        total = stats[0]["total"] if stats else 0
        records = [_to_question_record(document) for document in facet["unique"]]
        return records, total


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
