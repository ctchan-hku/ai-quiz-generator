from app.modules.student_stats.constants import NUM_QUARTILES


def quartile_group_indices(
    scores_per_student: list[int | float],
) -> tuple[list[int], list[int], list[int], list[int]]:
    n = len(scores_per_student)
    if n == 0:
        return ([], [], [], [])

    ranked_indices = sorted(
        range(n),
        key=lambda index: scores_per_student[index],
    )
    groups: list[list[int]] = [[], [], [], []]
    for rank_position, student_index in enumerate(ranked_indices):
        quartile = min(NUM_QUARTILES - 1, rank_position * NUM_QUARTILES // n)
        groups[quartile].append(student_index)
    return (groups[0], groups[1], groups[2], groups[3])
