from fastapi import HTTPException, Request
from motor.motor_asyncio import AsyncIOMotorDatabase


def get_database(request: Request) -> AsyncIOMotorDatabase:
    db = request.app.state.mongodb_database
    if db is None:
        raise HTTPException(
            status_code=503,
            detail=(
                "Database is disabled. Set MONGODB_CONNECTION_STRING to enable "
                "course lookups."
            ),
        )
    return db
