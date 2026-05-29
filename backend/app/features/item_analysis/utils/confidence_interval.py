import math

from app.features.item_analysis.constants import (
    CONFIDENCE_LEVEL_Z,
    FISHER_Z_SAMPLE_SIZE_OFFSET,
    MIN_SAMPLE_SIZE_FOR_CORRELATION_CI,
    MIN_SAMPLE_SIZE_FOR_MEAN_CI,
)


def confidence_interval_for_mean(
    values: list[float],
) -> tuple[float, float] | None:
    sample_size = len(values)
    if sample_size < MIN_SAMPLE_SIZE_FOR_MEAN_CI:
        return None

    mean = sum(values) / sample_size
    sum_squared_deviation = sum((value - mean) ** 2 for value in values)
    variance = sum_squared_deviation / (sample_size - 1)
    if variance == 0:
        return (mean, mean)

    margin = CONFIDENCE_LEVEL_Z * math.sqrt(variance / sample_size)
    return (mean - margin, mean + margin)


def confidence_interval_for_correlation(
    correlation: float,
    sample_size: int,
) -> tuple[float, float] | None:
    if sample_size < MIN_SAMPLE_SIZE_FOR_CORRELATION_CI:
        return None

    if correlation <= -1.0:
        return (-1.0, -1.0)
    if correlation >= 1.0:
        return (1.0, 1.0)

    fisher_z = math.atanh(correlation)
    standard_error = 1 / math.sqrt(sample_size - FISHER_Z_SAMPLE_SIZE_OFFSET)
    margin = CONFIDENCE_LEVEL_Z * standard_error
    return (
        math.tanh(fisher_z - margin),
        math.tanh(fisher_z + margin),
    )


def metric_index_bounds(
    point_estimate: float,
    confidence_bounds: tuple[float, float] | None,
    *,
    clamp_lower: float,
    clamp_upper: float,
) -> list[float]:
    if confidence_bounds is None:
        return [point_estimate, point_estimate]
    lower, upper = confidence_bounds
    return [
        max(clamp_lower, lower),
        min(clamp_upper, upper),
    ]
