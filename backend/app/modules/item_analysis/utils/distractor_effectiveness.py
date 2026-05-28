from app.modules.item_analysis.constants import (
    DISCRIMINATION_INDEX_CAP,
    DISCRIMINATION_WEIGHT,
    MIN_SELECTION_RATE,
    POINT_BISERIAL_CAP,
    POINT_BISERIAL_WEIGHT,
    SELECTION_RATE_CAP,
    SELECTION_WEIGHT,
)
from app.modules.item_analysis.utils.correlation import pearson_correlation


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

    bottom_count = sum(selection_flags[i] for i in bottom_quartile_indices)
    top_count = sum(selection_flags[i] for i in top_quartile_indices)
    bottom_rate = bottom_count / len(bottom_quartile_indices)
    top_rate = top_count / len(top_quartile_indices)
    return bottom_rate - top_rate


def _combine_effectiveness_components(
    selection_rate: float,
    discrimination_index: float,
    biserial_correlation: float,
) -> float:
    norm_rate = min(selection_rate / SELECTION_RATE_CAP, 1.0)
    norm_disc = min(max(discrimination_index, 0.0) / DISCRIMINATION_INDEX_CAP, 1.0)

    # We want distractors to negatively correlate with overall performance (good students avoid them).
    norm_corr = min(max(-biserial_correlation, 0.0) / POINT_BISERIAL_CAP, 1.0)

    # If distractor is ignored entirely, it is completely ineffective.
    if selection_rate < MIN_SELECTION_RATE:
        return 0.0

    return (
        norm_rate * SELECTION_WEIGHT
        + norm_disc * DISCRIMINATION_WEIGHT
        + norm_corr * POINT_BISERIAL_WEIGHT
    )
