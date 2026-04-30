import json

import pytest
from pydantic import ValidationError

from app.services.llm.full_quiz import FullQuizLlm


@pytest.fixture(autouse=True)
def _shuffle_identity_for_full_quiz_parse(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "app.services.llm.full_quiz.shuffle_option_order",
        lambda opts, ci: (list(opts), list(ci)),
    )


_parse_quiz = FullQuizLlm("_", 1).parse


def test_build_messages_with_topic_marks_topic_as_domain_only() -> None:
    messages = FullQuizLlm(
        topic="Cell biology",
        num_questions=2,
        few_shot_examples=["Case: A patient shows ATP depletion under hypoxia."],
    ).build_messages()
    user_content = messages[1]["content"]
    assert "examples must not be overshadowed by topic breadth alone" in user_content
    sys_content = messages[0]["content"]
    assert "# Guidelines" in sys_content
    assert "# Context" in sys_content
    assert sys_content.index("# Guidelines") < sys_content.index("# Context")
    assert "Topic domain boundary: Cell biology" in sys_content
    assert "Source priority (highest to lowest):" in sys_content
    assert "1) Examples (scenario style, detail level, reasoning pattern)" in sys_content
    assert "3) Topic" in sys_content
    assert "Topic is a domain label only." in sys_content
    assert "If topic conflicts with examples, keep the example pattern" in sys_content


def test_build_messages_without_topic_still_includes_priority_rules() -> None:
    messages = FullQuizLlm(
        topic="",
        num_questions=2,
        few_shot_examples=["Scenario: Evaluate trade-offs in a production outage."],
    ).build_messages()
    sys_content = messages[0]["content"]
    assert "# Guidelines" in sys_content
    assert "# Context" in sys_content
    assert "The user did not provide a topic." in sys_content
    assert "Source priority (highest to lowest):" in sys_content
    assert "examples must not be overshadowed by topic breadth alone" in messages[1]["content"]


def _mcq() -> dict:
    return {
        "question_type": "multiple_choice",
        "question": "Capital of France?",
        "options": ["Berlin", "Madrid", "Paris", "Rome"],
        "correct_indices": [2],
        "explanation": "Paris is the capital of France.",
    }


def test_parse_accepts_object_with_questions_key() -> None:
    payload = {"questions": [_mcq()]}
    raw = json.dumps(payload)
    schema = _parse_quiz(raw)
    assert len(schema.questions) == 1
    assert schema.questions[0].question_type == "multiple_choice"
    assert len(schema.questions[0].options) == 4


def test_parse_accepts_raw_list_of_questions() -> None:
    raw = json.dumps([_mcq()])
    schema = _parse_quiz(raw)
    assert len(schema.questions) == 1


def test_parse_strips_fences_then_validates() -> None:
    inner = json.dumps({"questions": [_mcq()]})
    raw = f"```json\n{inner}\n```"
    schema = _parse_quiz(raw)
    assert len(schema.questions) == 1


def test_parse_empty_questions_list() -> None:
    schema = _parse_quiz(json.dumps({"questions": []}))
    assert schema.questions == []


def test_parse_unexpected_top_level_shape() -> None:
    raw = json.dumps(_mcq())
    with pytest.raises(ValueError, match="Unexpected LLM output shape"):
        _parse_quiz(raw)


def test_parse_invalid_json() -> None:
    with pytest.raises(json.JSONDecodeError):
        _parse_quiz("{not json")


def test_parse_validation_error_bad_mc_question_one_option() -> None:
    bad = {
        "questions": [
            {
                "question_type": "multiple_choice",
                "question": "?",
                "options": ["solo"],
                "correct_indices": [0],
                "explanation": "x",
            }
        ]
    }
    with pytest.raises(ValidationError):
        _parse_quiz(json.dumps(bad))


def test_parse_accepts_two_options() -> None:
    payload = {
        "questions": [
            {
                "question_type": "multiple_choice",
                "question": "?",
                "options": ["a", "b"],
                "correct_indices": [1],
                "explanation": "x",
            }
        ]
    }
    schema = _parse_quiz(json.dumps(payload))
    assert len(schema.questions[0].options) == 2


def test_parse_validation_error_bad_mc_question_duplicate_correct_index() -> None:
    bad = {
        "questions": [
            {
                "question_type": "multiple_choice",
                "question": "?",
                "options": ["a", "b", "c", "d"],
                "correct_indices": [1, 1],
                "explanation": "x",
            }
        ]
    }
    with pytest.raises(ValidationError):
        _parse_quiz(json.dumps(bad))
