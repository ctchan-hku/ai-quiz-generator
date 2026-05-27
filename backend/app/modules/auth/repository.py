from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase

USERS_COLLECTION = "users"


class UserRepository:
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self._collection = db[USERS_COLLECTION]

    async def find_by_username(self, username: str) -> dict[str, Any] | None:
        return await self._collection.find_one(
            {"username": username},
            {"_id": 1, "username": 1, "password": 1},
        )
