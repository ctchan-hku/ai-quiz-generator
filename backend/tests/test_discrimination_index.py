from app.modules.data.student_stats.utils.confidence_interval import (
    confidence_interval_for_correlation,
    metric_index_bounds,
)
from app.modules.data.student_stats.utils.correlation import (
    corrected_point_biserial_correlation,
    pearson_correlation,
)


def _rest_of_test_scores(
    question_scores_per_student: list[int | float],
    total_test_scores_per_student: list[int | float],
) -> list[float]:
    return [
        float(total - question)
        for total, question in zip(
            total_test_scores_per_student,
            question_scores_per_student,
            strict=True,
        )
    ]


def test_discrimination_index_is_pearson_r_between_question_and_rest_of_test_scores() -> (
    None
):
    question_scores_per_student = [0, 0, 1, 1, 1, 1, 1, 1, 1, 1]
    total_test_scores_per_student = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    rest_of_test_scores_per_student = _rest_of_test_scores(
        question_scores_per_student,
        total_test_scores_per_student,
    )
    expected = pearson_correlation(
        [float(score) for score in question_scores_per_student],
        rest_of_test_scores_per_student,
    )

    index = corrected_point_biserial_correlation(
        question_scores_per_student,
        total_test_scores_per_student,
    )

    assert index == expected


def test_discrimination_index_can_be_negative() -> None:
    question_scores_per_student = [0, 0, 0, 0, 0, 1, 1, 1, 1, 1]
    total_test_scores_per_student = [10, 9, 8, 7, 6, 5, 4, 3, 2, 1]

    index = corrected_point_biserial_correlation(
        question_scores_per_student,
        total_test_scores_per_student,
    )

    assert index < 0


def test_discrimination_index_can_be_positive() -> None:
    question_scores_per_student = [0, 0, 1, 1, 1, 1, 1, 1, 1, 1]
    total_test_scores_per_student = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    index = corrected_point_biserial_correlation(
        question_scores_per_student,
        total_test_scores_per_student,
    )

    assert index > 0


def test_discrimination_index_stays_within_negative_one_and_one() -> None:
    cases = [
        ([0, 0, 0, 0, 0, 1, 1, 1, 1, 1], [10, 9, 8, 7, 6, 5, 4, 3, 2, 1]),
        ([0, 0, 1, 1, 1, 1, 1, 1, 1, 1], [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]),
        ([1, 0, 1, 0, 1, 0, 1, 0, 1, 0], [5, 5, 5, 5, 5, 5, 5, 5, 5, 5]),
        ([0, 1, 2, 3, 4, 5, 6, 7, 8, 9], [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]),
    ]
    for question_scores, total_scores in cases:
        index = corrected_point_biserial_correlation(question_scores, total_scores)
        assert -1.0 <= index <= 1.0


def test_discrimination_index_bounds_are_clamped_to_negative_one_and_one() -> None:
    question_scores_per_student = [0, 0, 0, 0, 0, 1, 1, 1, 1, 1]
    total_test_scores_per_student = [10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
    point_estimate = corrected_point_biserial_correlation(
        question_scores_per_student,
        total_test_scores_per_student,
    )
    confidence_bounds = confidence_interval_for_correlation(
        point_estimate,
        len(question_scores_per_student),
    )

    bounds = metric_index_bounds(
        point_estimate,
        confidence_bounds,
        clamp_lower=-1.0,
        clamp_upper=1.0,
    )

    assert len(bounds) == 2
    assert -1.0 <= bounds[0] <= bounds[1] <= 1.0
