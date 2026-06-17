from motor.motor_asyncio import AsyncIOMotorClient


def create_motor_client(mongodb_connection_string: str) -> AsyncIOMotorClient:
    return AsyncIOMotorClient(mongodb_connection_string)


async def ping_mongo_server(client: AsyncIOMotorClient) -> None:
    await client.admin.command("ping")
