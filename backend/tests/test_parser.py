import json

import pytest
from pydantic import ValidationError

from app.services.parser import _parse, _strip_fences


def _mcq() -> dict:
    return {
        "question_type": "multiple_choice",
        "question": "Capital of France?",
        "options": ["Berlin", "Madrid", "Paris", "Rome"],
        "correct_indices": [2],
        "explanation": "Paris is the capital of France.",
    }


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
    assert _strip_fences(raw) == expected


def test_parse_accepts_object_with_questions_key() -> None:
    payload = {"questions": [_mcq()]}
    raw = json.dumps(payload)
    schema = _parse(raw)
    assert len(schema.questions) == 1
    assert schema.questions[0].question_type == "multiple_choice"
    assert len(schema.questions[0].options) == 4


def test_parse_accepts_raw_list_of_questions() -> None:
    raw = json.dumps([_mcq()])
    schema = _parse(raw)
    assert len(schema.questions) == 1


def test_parse_strips_fences_then_validates() -> None:
    inner = json.dumps({"questions": [_mcq()]})
    raw = f"```json\n{inner}\n```"
    schema = _parse(raw)
    assert len(schema.questions) == 1


def test_parse_empty_questions_list() -> None:
    schema = _parse(json.dumps({"questions": []}))
    assert schema.questions == []


def test_parse_unexpected_top_level_shape() -> None:
    raw = json.dumps(_mcq())
    with pytest.raises(ValueError, match="Unexpected LLM output shape"):
        _parse(raw)


def test_parse_invalid_json() -> None:
    with pytest.raises(json.JSONDecodeError):
        _parse("{not json")


def test_parse_validation_error_bad_mcq() -> None:
    bad = {
        "questions": [
            {
                "question_type": "multiple_choice",
                "question": "?",
                "options": ["a", "b"],
                "correct_indices": [0],
                "explanation": "x",
            }
        ]
    }
    with pytest.raises(ValidationError):
        _parse(json.dumps(bad))
