"""``MultipleChoiceQuestion`` validators and ``constants.mc_question`` counts."""

import pytest
from pydantic import ValidationError

from app.constants.mc_question import MC_QUESTION_OPTION_COUNT_MAX, MC_QUESTION_OPTION_COUNT_MIN
from app.models.mc_question import MultipleChoiceQuestion


def _valid(**kwargs: object) -> MultipleChoiceQuestion:
    defaults = dict(
        question_type="multiple_choice",
        question="Q?",
        options=["a", "b", "c", "d"],
        correct_indices=[0],
        explanation="because",
    )
    defaults.update(kwargs)
    return MultipleChoiceQuestion.model_validate(defaults)


def test_defaults_four_options_accepted() -> None:
    q = _valid()
    assert len(q.options) == 4


def test_two_through_six_options_accepted() -> None:
    for n in range(MC_QUESTION_OPTION_COUNT_MIN, MC_QUESTION_OPTION_COUNT_MAX + 1):
        opts = [f"opt{i}" for i in range(n)]
        q = _valid(options=opts, correct_indices=[0])
        assert len(q.options) == n


def test_seventh_option_truncated_to_max_with_indices_remapped(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.helpers.options.secrets.choice", lambda removable: removable[0]
    )
    q = _valid(options=[str(i) for i in range(7)], correct_indices=[6])
    assert len(q.options) == MC_QUESTION_OPTION_COUNT_MAX
    assert q.correct_indices == [5]


def test_empty_correct_indices_rejected() -> None:
    with pytest.raises(ValidationError):
        _valid(correct_indices=[])


def test_multi_correct_when_valid() -> None:
    q = _valid(options=["a", "b", "c", "d"], correct_indices=[0, 3])
    assert q.correct_indices == [0, 3]


def test_index_out_of_range_rejected() -> None:
    with pytest.raises(ValidationError):
        _valid(options=["a", "b"], correct_indices=[2])
