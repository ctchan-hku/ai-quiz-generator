def pearson_correlation(x_values: list[float], y_values: list[float]) -> float:
    n = len(x_values)
    if n != len(y_values) or n < 2:
        return 0.0

    mean_x = sum(x_values) / n
    mean_y = sum(y_values) / n
    diff_x = [x - mean_x for x in x_values]
    diff_y = [y - mean_y for y in y_values]
    sum_xy = sum(dx * dy for dx, dy in zip(diff_x, diff_y, strict=True))
    sum_xx = sum(dx * dx for dx in diff_x)
    sum_yy = sum(dy * dy for dy in diff_y)
    if sum_xx == 0 or sum_yy == 0:
        return 0.0
    return sum_xy / (sum_xx * sum_yy) ** 0.5


def corrected_point_biserial_correlation(
    question_scores_per_student: list[int | float],
    total_test_scores_per_student: list[int | float],
) -> float:
    rest_of_test_scores_per_student = [
        total - question
        for total, question in zip(
            total_test_scores_per_student,
            question_scores_per_student,
            strict=True,
        )
    ]
    return pearson_correlation(
        [float(score) for score in question_scores_per_student],
        [float(score) for score in rest_of_test_scores_per_student],
    )
