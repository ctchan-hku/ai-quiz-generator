from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.modules.data.student_stats.models import CourseGroupSummary

COURSE_GROUPS_COLLECTION = "course_groups"


class CourseGroupRepository:
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self._collection = db[COURSE_GROUPS_COLLECTION]

    async def find_owned_by_user(self, user_id: str) -> list[CourseGroupSummary]:
        cursor = self._collection.find(
            self._owner_query(user_id),
            {"_id": 1, "name": 1},
        )
        documents = await cursor.to_list(length=None)
        return [
            CourseGroupSummary(id=str(document["_id"]), name=document["name"])
            for document in documents
            if "name" in document
        ]

    @staticmethod
    def _owner_query(user_id: str) -> dict:
        if ObjectId.is_valid(user_id):
            object_id = ObjectId(user_id)
            return {"owner": {"$in": [user_id, object_id]}}
        return {"owner": user_id}
