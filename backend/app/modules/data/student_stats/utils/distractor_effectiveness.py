from app.modules.data.student_stats.utils.correlation import pearson_correlation

_TOP_BOTTOM_GROUP_FRACTION = 0.27
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
) -> float:
    discrimination_index = _distractor_discrimination_index(
        selection_flags,
        total_test_scores_per_student,
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


def _top_and_bottom_group_indices(
    total_test_scores_per_student: list[int | float],
    *,
    fraction: float = _TOP_BOTTOM_GROUP_FRACTION,
) -> tuple[list[int], list[int]]:
    n = len(total_test_scores_per_student)
    if n == 0:
        return [], []

    group_size = max(1, int(n * fraction))
    ranked_indices = sorted(
        range(n),
        key=lambda index: total_test_scores_per_student[index],
    )
    return ranked_indices[:group_size], ranked_indices[-group_size:]


def _distractor_discrimination_index(
    selection_flags: list[float],
    total_test_scores_per_student: list[int | float],
) -> float:
    bottom_indices, top_indices = _top_and_bottom_group_indices(
        total_test_scores_per_student,
    )
    if not bottom_indices or not top_indices:
        return 0.0

    proportion_in_bottom = sum(selection_flags[i] for i in bottom_indices) / len(
        bottom_indices,
    )
    proportion_in_top = sum(selection_flags[i] for i in top_indices) / len(
        top_indices,
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
