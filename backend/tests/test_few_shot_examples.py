import pytest
from fastapi import HTTPException

from app.services.few_shot import FEW_SHOT_MAX_CHARS, normalize_few_shot_examples


def test_normalize_none_returns_empty() -> None:
    assert normalize_few_shot_examples(None) == []


def test_normalize_empty_list() -> None:
    assert normalize_few_shot_examples([]) == []


def test_normalize_trims_and_drops_empty() -> None:
    assert normalize_few_shot_examples(["  a  ", "", "  b"]) == ["a", "b"]


def test_normalize_max_three() -> None:
    assert normalize_few_shot_examples(["1", "2", "3"]) == ["1", "2", "3"]


def test_normalize_rejects_four_non_empty() -> None:
    with pytest.raises(HTTPException) as exc_info:
        normalize_few_shot_examples(["a", "b", "c", "d"])
    assert exc_info.value.status_code == 422


def test_normalize_rejects_too_long() -> None:
    long_s = "x" * (FEW_SHOT_MAX_CHARS + 1)
    with pytest.raises(HTTPException) as exc_info:
        normalize_few_shot_examples([long_s])
    assert exc_info.value.status_code == 422


def test_normalize_accepts_max_length() -> None:
    s = "x" * FEW_SHOT_MAX_CHARS
    assert normalize_few_shot_examples([s]) == [s]
