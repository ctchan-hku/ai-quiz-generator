"""Tests for ``app.helpers.options`` (MCQ option truncation)."""

from app.models.mcq_constraints import MCQ_OPTION_COUNT_MAX
from app.helpers.options import truncate_options


def test_protects_random_one_of_two_correct_when_truncating(monkeypatch) -> None:
    """Mock forces keep=last correct index; removals use smallest removable index."""
    calls: list[tuple[int, ...]] = []

    def fake_choice(removable_like: object) -> int:
        seq = tuple(removable_like)
        calls.append(seq)
        if len(calls) == 1:
            return 6
        assert 6 not in seq
        return seq[0]

    monkeypatch.setattr("app.helpers.options.secrets.choice", fake_choice)
    opts = [str(i) for i in range(7)]
    out_o, out_ci = truncate_options(opts, [1, 6], max_opts=6)
    assert len(out_o) == MCQ_OPTION_COUNT_MAX
    assert set(calls[0]) == {1, 6}
    assert out_ci == [0, 5]
