"""Cryptographic shuffle of MCQ option rows for generation flows."""

from __future__ import annotations

import secrets


def shuffle_option_order(
    options: list[str], correct_indices: list[int]
) -> tuple[list[str], list[int]]:
    """Cryptographically shuffle option rows and remap ``correct_indices``.

    Let ``order[k]`` be which **old** index occupies **new** slot ``k`` after shuffle:
    ``new_options[k] == options[order[k]]``. Each old correct index ``c`` moves to new slot
    ``order.index(c)``.
    """
    n = len(options)
    order = list(range(n))
    rng = secrets.SystemRandom()
    rng.shuffle(order)
    new_options = [options[order[k]] for k in range(n)]
    new_correct_indices = sorted(order.index(c) for c in correct_indices)
    return new_options, new_correct_indices
