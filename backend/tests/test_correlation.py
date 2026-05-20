import math

import pytest
from scipy.stats import pearsonr

from app.modules.data.student_stats.utils.correlation import (
    corrected_point_biserial,
    pearson_correlation,
)


def test_pearson_correlation_matches_scipy() -> None:
    x_values = [1.0, 2.0, 3.0, 4.0, 5.0]
    y_values = [2.0, 4.0, 5.0, 4.0, 5.0]
    expected, _ = pearsonr(x_values, y_values)

    assert pearson_correlation(x_values, y_values) == pytest.approx(expected)


def test_pearson_correlation_returns_zero_when_variance_is_zero() -> None:
    x_values = [1.0, 1.0, 1.0]
    y_values = [2.0, 3.0, 4.0]
    scipy_result, _ = pearsonr(x_values, y_values)

    assert math.isnan(scipy_result)
    assert pearson_correlation(x_values, y_values) == 0.0


def test_corrected_point_biserial_matches_scipy() -> None:
    item_scores = [0, 1, 0, 1, 1, 0, 1, 0]
    total_test_scores = [2, 5, 3, 6, 7, 2, 8, 1]
    rest_of_test_scores = [
        total - item for total, item in zip(total_test_scores, item_scores, strict=True)
    ]
    expected, _ = pearsonr(item_scores, rest_of_test_scores)

    assert corrected_point_biserial(item_scores, total_test_scores) == pytest.approx(
        expected,
    )


def test_corrected_point_biserial_returns_zero_when_item_scores_are_constant() -> None:
    item_scores = [1, 1, 1, 1]
    total_test_scores = [3, 4, 5, 6]
    scipy_rest = [t - i for t, i in zip(total_test_scores, item_scores, strict=True)]
    scipy_result, _ = pearsonr(item_scores, scipy_rest)

    assert math.isnan(scipy_result)
    assert corrected_point_biserial(item_scores, total_test_scores) == 0.0
