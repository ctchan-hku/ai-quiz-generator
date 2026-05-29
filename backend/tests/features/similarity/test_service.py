from unittest.mock import MagicMock

from app.features.similarity.models import FewShotExample
from app.features.similarity.service import SimilarityService


def test_find_similar_for_examples_returns_top_matches():
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

    service = SimilarityService(vector_store=mock_store, top_k=3)
    response = service.find_similar_for_examples(
        [FewShotExample(question="Example?", options=["1", "2"])]
    )

    assert len(response.results) == 1
    assert response.results[0].example_index == 0
    assert len(response.results[0].matches) == 1
    assert response.results[0].matches[0].question_id == "q1"
    mock_store.similarity_search_with_score.assert_called_once()
