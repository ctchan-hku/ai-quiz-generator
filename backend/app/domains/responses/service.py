from app.domains.responses.models import ResponseRecord
from app.domains.responses.repository import ResponseRepository


class ResponseService:
    def __init__(self, repository: ResponseRepository) -> None:
        self._repository = repository

    async def list_by_test_id(self, test_id: str) -> list[ResponseRecord]:
        return await self._repository.find_by_test_id(test_id)
