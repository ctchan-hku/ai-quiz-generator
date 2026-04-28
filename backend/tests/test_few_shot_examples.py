import pytest
from fastapi import HTTPException

from app.services.prompt_sections.few_shot import FEW_SHOT_FORMATTER, FEW_SHOT_MAX_CHARS
from app.services.prompt_sections.section_formatter import SectionFormatter


def test_normalize_none_returns_empty() -> None:
    assert FEW_SHOT_FORMATTER.normalize(None) == []


def test_normalize_empty_list() -> None:
    assert FEW_SHOT_FORMATTER.normalize([]) == []


def test_normalize_trims_and_drops_empty() -> None:
    assert FEW_SHOT_FORMATTER.normalize(["  a  ", "", "  b"]) == ["a", "b"]


def test_normalize_max_three() -> None:
    assert FEW_SHOT_FORMATTER.normalize(["1", "2", "3"]) == ["1", "2", "3"]


def test_normalize_rejects_four_non_empty() -> None:
    with pytest.raises(HTTPException) as exc_info:
        FEW_SHOT_FORMATTER.normalize(["a", "b", "c", "d"])
    assert exc_info.value.status_code == 422


def test_normalize_rejects_too_long() -> None:
    long_s = "x" * (FEW_SHOT_MAX_CHARS + 1)
    with pytest.raises(HTTPException) as exc_info:
        FEW_SHOT_FORMATTER.normalize([long_s])
    assert exc_info.value.status_code == 422


def test_normalize_accepts_max_length() -> None:
    s = "x" * FEW_SHOT_MAX_CHARS
    assert FEW_SHOT_FORMATTER.normalize([s]) == [s]


def test_few_shot_addon_satisfies_section_formatter() -> None:
    assert isinstance(FEW_SHOT_FORMATTER, SectionFormatter)


    def test_user_message_supplement_empty_when_no_examples() -> None:
        pass

    def test_user_message_supplement_present_when_examples() -> None:
        pass
