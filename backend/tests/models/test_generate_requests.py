"""GenerateQuizRequest validation for topic vs few-shot."""

import pytest
from pydantic import ValidationError

from app.models.generate_requests import GenerateQuizRequest


def _valid(**kwargs: object) -> GenerateQuizRequest:
    defaults: dict[str, object] = dict(
        topic="Algebra",
        model="gpt-4o",
        num_questions=1,
    )
    defaults.update(kwargs)
    return GenerateQuizRequest.model_validate(defaults)


def test_topic_only_accepted() -> None:
    q = _valid()
    assert q.topic == "Algebra"


def test_topic_stripped() -> None:
    q = _valid(topic="  x  ")
    assert q.topic == "x"


def test_empty_topic_with_few_shot_accepted() -> None:
    q = _valid(topic="", few_shot_examples=["Sample Q: ..."])
    assert q.topic == ""
    assert q.few_shot_examples == ["Sample Q: ..."]


def test_empty_topic_whitespace_only_needs_example() -> None:
    with pytest.raises(ValidationError):
        _valid(topic="   ", few_shot_examples=None)


def test_both_empty_rejected() -> None:
    with pytest.raises(ValidationError):
        _valid(topic="", few_shot_examples=[])

    with pytest.raises(ValidationError):
        _valid(topic="", few_shot_examples=["", "  "])
