from app.modules.data.student_stats.models import ResponseListResponse
from app.modules.data.student_stats.repositories.response_repository import (
    ResponseRepository,
)


class ResponseService:
    def __init__(self, repository: ResponseRepository) -> None:
        self._repository = repository

    async def list_by_test_id(self, test_id: str) -> ResponseListResponse:
        responses = await self._repository.find_by_test_id(test_id)
        return ResponseListResponse(responses=responses)
