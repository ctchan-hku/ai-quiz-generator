from app.modules.data.student_stats.utils.correlation import pearson_correlation

_MIN_SELECTION_RATE = 0.05
_SELECTION_RATE_CAP = 0.20
_DISCRIMINATION_INDEX_CAP = 0.20
_POINT_BISERIAL_CAP = 0.30
_SELECTION_WEIGHT = 0.3
_DISCRIMINATION_WEIGHT = 0.4
_POINT_BISERIAL_WEIGHT = 0.3


def distractor_effectiveness(
    selection_rate: float,
    selection_flags: list[float],
    total_test_scores_per_student: list[int | float],
    bottom_and_top_quartile_indices: tuple[list[int], list[int]],
) -> float:
    discrimination_index = _distractor_discrimination_index(
        selection_flags,
        bottom_and_top_quartile_indices,
    )
    biserial_correlation = pearson_correlation(
        selection_flags,
        [float(score) for score in total_test_scores_per_student],
    )
    return _combine_effectiveness_components(
        selection_rate,
        discrimination_index,
        biserial_correlation,
    )


def _distractor_discrimination_index(
    selection_flags: list[float],
    bottom_and_top_quartile_indices: tuple[list[int], list[int]],
) -> float:
    bottom_quartile_indices, top_quartile_indices = bottom_and_top_quartile_indices
    if not bottom_quartile_indices or not top_quartile_indices:
        return 0.0

    proportion_in_bottom = sum(
        selection_flags[i] for i in bottom_quartile_indices
    ) / len(bottom_quartile_indices)
    proportion_in_top = sum(selection_flags[i] for i in top_quartile_indices) / len(
        top_quartile_indices,
    )
    return proportion_in_bottom - proportion_in_top


def _combine_effectiveness_components(
    selection_rate: float,
    discrimination_index: float,
    biserial_correlation: float,
) -> float:
    if selection_rate >= _MIN_SELECTION_RATE:
        selection_component = min(selection_rate / _SELECTION_RATE_CAP, 1.0)
    else:
        selection_component = 0.0

    discrimination_component = max(
        0.0,
        min(discrimination_index / _DISCRIMINATION_INDEX_CAP, 1.0),
    )
    biserial_component = max(
        0.0,
        min(abs(biserial_correlation) / _POINT_BISERIAL_CAP, 1.0),
    )

    effectiveness = (
        _SELECTION_WEIGHT * selection_component
        + _DISCRIMINATION_WEIGHT * discrimination_component
        + _POINT_BISERIAL_WEIGHT * biserial_component
    )
    return round(effectiveness, 2)
