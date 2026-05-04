import json

import pytest
from pydantic import ValidationError

from app.models.mc_question import MultipleChoiceQuestion
from app.services.llm import SingleMcqLlm


@pytest.fixture(autouse=True)
def _shuffle_identity_for_single_mc_question_parse(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "app.services.llm.single_mcq.shuffle_option_order",
        lambda opts, ci: (list(opts), list(ci)),
    )


def _sample_mc_question() -> MultipleChoiceQuestion:
    return MultipleChoiceQuestion(
        question_type="multiple_choice",
        question="Capital of France?",
        options=["Berlin", "Madrid", "Paris", "Rome"],
        correct_indices=[2],
        explanation="Paris is the capital.",
    )


_parse_mc_question = SingleMcqLlm(
    ".", _sample_mc_question(), ""
).parse


def test_build_messages_includes_topic_and_target_and_default_hint_when_no_comment() -> None:
    q = _sample_mc_question()
    messages = SingleMcqLlm("European capitals", q, "").build_messages()
    assert messages[0]["role"] == "system"
    sys_content = messages[0]["content"]
    assert "European capitals" in sys_content
    assert "# Context" in sys_content
    assert "Topic domain boundary:" in sys_content
    assert "correct_indices" in sys_content and "explanation" in sys_content.lower()
    assert "sibling" not in sys_content.lower()
    user_content = messages[1]["content"]
    assert "Capital of France?" in user_content
    assert "Berlin" in user_content


def test_build_messages_omits_context_when_topic_empty() -> None:
    q = _sample_mc_question()
    messages = SingleMcqLlm("", q, "").build_messages()
    assert "# Context" not in messages[0]["content"]


def test_build_messages_includes_editor_comment_when_comment_set() -> None:
    q = _sample_mc_question()
    messages = SingleMcqLlm("Capitals", q, "Make it harder.").build_messages()
    user_content = messages[1]["content"]
    assert "Editor comment:" in user_content
    assert "Make it harder." in user_content


def test_parse_single_mc_question_validates_one_object() -> None:
    raw = json.dumps(
        {
            "question_type": "multiple_choice",
            "question": "x?",
            "options": ["a", "b", "c", "d"],
            "correct_indices": [0],
            "explanation": "e",
        }
    )
    out = _parse_mc_question(raw)
    assert out.question == "x?"


def test_parse_single_mc_question_rejects_wrapped_question_key() -> None:
    inner = {
        "question_type": "multiple_choice",
        "question": "x?",
        "options": ["a", "b", "c", "d"],
        "correct_indices": [0],
        "explanation": "e",
    }
    with pytest.raises(ValidationError):
        _parse_mc_question(json.dumps({"question": inner}))


def test_parse_single_mc_question_rejects_bare_list_shape() -> None:
    with pytest.raises((ValidationError, ValueError)):
        _parse_mc_question("[]")
