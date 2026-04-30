import pytest
from fastapi import HTTPException

from app.services.prompt_sections.section_formatter import SectionFormatter
from app.services.prompt_sections.user_instructions import (
    USER_INSTRUCTION_LINE_MAX_CHARS,
    USER_INSTRUCTIONS_FORMATTER,
    USER_INSTRUCTIONS_MAX,
)


def test_normalize_user_instructions_none() -> None:
    assert USER_INSTRUCTIONS_FORMATTER.normalize(None) == []


def test_normalize_user_instructions_trims_skips_empty() -> None:
    assert USER_INSTRUCTIONS_FORMATTER.normalize(["  hello  ", "", "there"]) == ["hello", "there"]


def test_normalize_user_instructions_too_long_raises() -> None:
    bad = ["x" * (USER_INSTRUCTION_LINE_MAX_CHARS + 1)]
    with pytest.raises(HTTPException) as excinfo:
        USER_INSTRUCTIONS_FORMATTER.normalize(bad)
    assert excinfo.value.status_code == 422


def test_normalize_user_instructions_too_many_raises() -> None:
    raw = ["a"] * (USER_INSTRUCTIONS_MAX + 1)
    with pytest.raises(HTTPException) as excinfo:
        USER_INSTRUCTIONS_FORMATTER.normalize(raw)
    assert excinfo.value.status_code == 422


def test_format_user_instructions_section_empty_returns_empty() -> None:
    assert USER_INSTRUCTIONS_FORMATTER.format_section([]) == ""


def test_format_user_instructions_section_numbered_only() -> None:
    text = USER_INSTRUCTIONS_FORMATTER.format_section(["focus on dates", "use SI units"])
    assert "focus on dates" in text
    assert "use SI units" in text
    assert text.startswith("Additional quiz instructions:\n")
    assert "1. focus on dates" in text
    assert "2. use SI units" in text


def test_format_section_is_not_merged_with_question_base() -> None:
    """Merge with MCQ schema text stays in ``FullQuizLlm`` only."""
    block = USER_INSTRUCTIONS_FORMATTER.format_section(["one rule"])
    assert "MultipleChoiceQuestion" not in block


def test_user_instructions_addon_satisfies_section_formatter() -> None:
    assert isinstance(USER_INSTRUCTIONS_FORMATTER, SectionFormatter)
