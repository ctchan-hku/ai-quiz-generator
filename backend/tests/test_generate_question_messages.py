import json

import pytest
from pydantic import ValidationError

from app.models.schemas import MultipleChoiceQuestion
from app.helpers.question_data import format_question
from app.services.llm import SingleMcqLlm


def _sample_mcq() -> MultipleChoiceQuestion:
    return MultipleChoiceQuestion(
        question_type="multiple_choice",
        question="Capital of France?",
        options=["Berlin", "Madrid", "Paris", "Rome"],
        correct_indices=[2],
        explanation="Paris is the capital.",
    )


_parse_mcq = SingleMcqLlm(".", _sample_mcq(), None).parse


def test_format_question_for_prompt_labels_options_with_letters() -> None:
    text = format_question(_sample_mcq())
    assert "A. Berlin" in text
    assert "B. Madrid" in text
    assert "C. Paris" in text
    assert "D. Rome" in text
    assert "[0]" not in text


def test_build_messages_includes_topic_and_target_and_default_hint_when_no_comment() -> None:
    q = _sample_mcq()
    messages = SingleMcqLlm("European capitals", q, None).build_messages()
    assert messages[0]["role"] == "system"
    sys_content = messages[0]["content"]
    assert "European capitals" in sys_content
    assert "Capital of France?" in sys_content
    assert "Berlin" in sys_content
    assert "correct answer" in sys_content.lower() and "explanation" in sys_content.lower()
    assert "sibling" not in sys_content.lower()


def test_build_messages_includes_editor_comment_when_comment_set() -> None:
    q = _sample_mcq()
    messages = SingleMcqLlm("Capitals", q, "Make it harder.").build_messages()
    sys_content = messages[0]["content"]
    assert "Editor comment:" in sys_content
    assert "Make it harder." in sys_content


def test_parse_single_mcq_validates_one_object() -> None:
    raw = json.dumps(
        {
            "question_type": "multiple_choice",
            "question": "x?",
            "options": ["a", "b", "c", "d"],
            "correct_indices": [0],
            "explanation": "e",
        }
    )
    out = _parse_mcq(raw)
    assert out.question == "x?"


def test_parse_single_mcq_rejects_wrapped_question_key() -> None:
    inner = {
        "question_type": "multiple_choice",
        "question": "x?",
        "options": ["a", "b", "c", "d"],
        "correct_indices": [0],
        "explanation": "e",
    }
    with pytest.raises(ValidationError):
        _parse_mcq(json.dumps({"question": inner}))


def test_parse_single_mcq_rejects_bare_mcq_list_shape() -> None:
    with pytest.raises((ValidationError, ValueError)):
        _parse_mcq("[]")
