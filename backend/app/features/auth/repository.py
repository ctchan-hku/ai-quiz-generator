from typing import Any

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

USERS_COLLECTION = "users"


class UserRepository:
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self._collection = db[USERS_COLLECTION]

    async def find_by_id(self, user_id: str) -> dict[str, Any] | None:
        query = (
            {"_id": ObjectId(user_id)}
            if ObjectId.is_valid(user_id)
            else {"_id": user_id}
        )
        return await self._collection.find_one(query, {"_id": 1, "username": 1})
