from app.modules.data.student_stats.utils.correlation import pearson_correlation

TOP_BOTTOM_GROUP_FRACTION = 0.27
MIN_SELECTION_RATE = 0.05
SELECTION_RATE_CAP = 0.20
DISCRIMINATION_INDEX_CAP = 0.20
POINT_BISERIAL_CAP = 0.30
SELECTION_WEIGHT = 0.3
DISCRIMINATION_WEIGHT = 0.4
POINT_BISERIAL_WEIGHT = 0.3


def top_and_bottom_group_indices(
    total_test_scores: list[int | float],
    *,
    fraction: float = TOP_BOTTOM_GROUP_FRACTION,
) -> tuple[list[int], list[int]]:
    n = len(total_test_scores)
    if n == 0:
        return [], []

    group_size = max(1, int(n * fraction))
    ranked_indices = sorted(range(n), key=lambda index: total_test_scores[index])
    return ranked_indices[:group_size], ranked_indices[-group_size:]


def distractor_discrimination_index(
    chose_option: list[float],
    total_test_scores: list[int | float],
) -> float:
    bottom_indices, top_indices = top_and_bottom_group_indices(total_test_scores)
    if not bottom_indices or not top_indices:
        return 0.0

    proportion_in_bottom = sum(chose_option[i] for i in bottom_indices) / len(
        bottom_indices,
    )
    proportion_in_top = sum(chose_option[i] for i in top_indices) / len(top_indices)
    return proportion_in_bottom - proportion_in_top


def point_biserial_for_distractor(
    chose_option: list[float],
    total_test_scores: list[int | float],
) -> float:
    return pearson_correlation(
        chose_option,
        [float(score) for score in total_test_scores],
    )


def distractor_effectiveness_score(
    selection_rate: float,
    distractor_discrimination_index_value: float,
    point_biserial: float,
) -> float:
    if selection_rate >= MIN_SELECTION_RATE:
        selection_component = min(selection_rate / SELECTION_RATE_CAP, 1.0)
    else:
        selection_component = 0.0

    discrimination_component = max(
        0.0,
        min(distractor_discrimination_index_value / DISCRIMINATION_INDEX_CAP, 1.0),
    )
    point_biserial_component = max(
        0.0,
        min(abs(point_biserial) / POINT_BISERIAL_CAP, 1.0),
    )

    effectiveness = (
        SELECTION_WEIGHT * selection_component
        + DISCRIMINATION_WEIGHT * discrimination_component
        + POINT_BISERIAL_WEIGHT * point_biserial_component
    )
    return round(effectiveness, 2)
