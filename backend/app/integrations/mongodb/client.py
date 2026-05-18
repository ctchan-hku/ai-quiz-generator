from motor.motor_asyncio import AsyncIOMotorClient


def create_motor_client(mongodb_uri: str) -> AsyncIOMotorClient:
    return AsyncIOMotorClient(mongodb_uri)


async def ping_mongo_server(client: AsyncIOMotorClient) -> None:
    await client.admin.command("ping")
