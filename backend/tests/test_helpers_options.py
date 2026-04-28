"""Tests for ``app.helpers.options`` (MCQ option truncation + shuffle)."""

from app.models.mcq_constraints import MCQ_OPTION_COUNT_MAX
from app.helpers.options import shuffle_option_order, truncate_options


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


def test_shuffle_preserves_length_and_multiset(monkeypatch) -> None:
    def fake_shuffle(_self, seq: list[int]) -> None:
        seq[:] = [2, 0, 1]

    monkeypatch.setattr("app.helpers.options.secrets.SystemRandom.shuffle", fake_shuffle)
    options = ["a", "b", "c"]
    new_o, new_ci = shuffle_option_order(options, [0])
    assert len(new_o) == 3
    assert sorted(new_o) == ["a", "b", "c"]
    assert new_ci == [1]


def test_shuffle_maps_multiple_correct_indices(monkeypatch) -> None:
    def fake_shuffle(_self, seq: list[int]) -> None:
        seq[:] = [3, 2, 1, 0]

    monkeypatch.setattr("app.helpers.options.secrets.SystemRandom.shuffle", fake_shuffle)
    options = ["w", "x", "y", "z"]
    new_o, new_ci = shuffle_option_order(options, [0, 3])
    assert new_o == ["z", "y", "x", "w"]
    assert new_ci == [0, 3]


def test_shuffle_full_quiz_roundtrip_invariant(monkeypatch) -> None:
    """Paris stays the correct label after shuffle (fixed permutation)."""
    from app.services.llm.full_quiz import FullQuizLlm

    def fake_shuffle(_self, seq: list[int]) -> None:
        seq[:] = [1, 2, 3, 0]

    monkeypatch.setattr("app.helpers.options.secrets.SystemRandom.shuffle", fake_shuffle)
    raw = (
        '{"questions":[{"question_type":"multiple_choice","question":"?",'
        '"options":["Berlin","Madrid","Paris","Rome"],"correct_indices":[2],'
        '"explanation":"because"}]}'
    )
    quiz = FullQuizLlm("_", 1).parse(raw)
    q = quiz.questions[0]
    assert q.options[1] == "Paris"
    assert q.correct_indices == [1]
