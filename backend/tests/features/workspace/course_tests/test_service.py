from unittest.mock import MagicMock

from app.features.workspace.course_tests.service import FewShotSearchService


def test_find_few_shots_returns_top_matches():
    mock_store = MagicMock()
    mock_store.similarity_search_with_score.return_value = [
        (
            MagicMock(
                metadata={
                    "question_id": "q1",
                    "prompt": "Stored question",
                    "options": ["A", "B"],
                }
            ),
            0.12,
        )
    ]

    service = FewShotSearchService(vector_store=mock_store, top_k=3)
    results = service.find_few_shots(["Which organelle produces ATP?"])

    assert len(results) == 1
    assert results[0].index == 0
    assert results[0].prompt == "Which organelle produces ATP?"
    assert len(results[0].matches) == 1
    assert results[0].matches[0].question_id == "q1"
    assert results[0].matches[0].score == 0.12
    mock_store.similarity_search_with_score.assert_called_once_with(
        "Which organelle produces ATP?",
        k=3,
    )
