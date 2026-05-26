import logging

from app.modules.data.student_stats.repositories.test_repository import TestRepository

logger = logging.getLogger(__name__)


class TestService:
    __test__ = False

    def __init__(self, repository: TestRepository | None) -> None:
        self._repository = repository

    async def log_test_names(self, test_ids: list[str]) -> None:
        if not test_ids:
            return
        if self._repository is None:
            logger.info(
                "Tests (MongoDB disabled): %s",
                test_ids,
            )
            return
        tests = await self._repository.find_by_ids(test_ids)
        names_by_id = {test.id: test.name for test in tests}
        labels = [
            names_by_id[test_id] if test_id in names_by_id else f"<unknown:{test_id}>"
            for test_id in test_ids
        ]
        logger.info("Tests: %s", ", ".join(labels))
