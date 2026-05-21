from app.modules.data.student_stats.utils.distractor_effectiveness import (
    distractor_discrimination_index,
    distractor_effectiveness_score,
    top_and_bottom_group_indices,
)


def test_top_and_bottom_group_indices() -> None:
    scores = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    bottom, top = top_and_bottom_group_indices(scores, fraction=0.27)

    assert bottom == [0, 1]
    assert top == [8, 9]


def test_distractor_discrimination_index_prefers_bottom_group() -> None:
    total_test_scores = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    chose_option = [1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

    assert distractor_discrimination_index(chose_option, total_test_scores) > 0


def test_distractor_effectiveness_score_ignores_low_selection_component() -> None:
    with_low_selection = distractor_effectiveness_score(0.04, 0.15, -0.25)
    without_selection_component = distractor_effectiveness_score(
        0.0,
        0.15,
        -0.25,
    )

    assert with_low_selection == without_selection_component


def test_distractor_effectiveness_score_is_rounded_to_two_decimals() -> None:
    score = distractor_effectiveness_score(0.10, 0.10, -0.15)

    assert score == round(score, 2)
