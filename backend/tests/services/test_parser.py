import pytest

from app.services.parser import strip_fences


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ('```json\n{"a": 1}\n```', '{"a": 1}'),
        ('```JSON\n{"a": 1}\n```', '{"a": 1}'),
        ("```\n[1, 2]\n```", "[1, 2]"),
        ('  {"x": 1}  ', '{"x": 1}'),
        ("no fences here", "no fences here"),
    ],
)
def test_strip_fences_removes_markdown_wrapper(raw: str, expected: str) -> None:
    assert strip_fences(raw) == expected
