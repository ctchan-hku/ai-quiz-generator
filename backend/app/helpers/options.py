"""MCQ option list trimming against max count while preserving one randomly chosen correct row."""

from __future__ import annotations

import secrets
from typing import Any

from app.models.mcq_constraints import MCQ_OPTION_COUNT_MAX


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


def truncate_options(
    options: list[Any],
    correct_indices: list[Any],
    max_opts: int = MCQ_OPTION_COUNT_MAX,
) -> tuple[list[Any], list[int]]:
    """Remove random options until ``len(options) <= max_opts``.

    Picks uniformly at random **one distinct** correct index before loop; only that slot is never
    removed. Each removal uniformly picks among all other indices (other correct lines and distractors).

    If ``correct_indices`` cannot be coerced to ints or is empty, returns the inputs unchanged so
    normal validation reports the error.

    Raises ``ValueError`` only if truncation cannot shrink (unexpected invariant break).
    """
    opts = list(options)
    try:
        ci_ints = [int(c) for c in correct_indices]
    except (TypeError, ValueError):
        return opts, correct_indices  # type: ignore[return-value]

    if not ci_ints:
        return opts, correct_indices  # type: ignore[return-value]

    distinct_correct = tuple(set(ci_ints))
    keep_correct = secrets.choice(distinct_correct)
    ci = ci_ints
    max_opts_val = max_opts

    while len(opts) > max_opts_val:
        n = len(opts)
        removable = [i for i in range(n) if i != keep_correct]
        if not removable:
            raise ValueError(
                "cannot truncate options without removing protected correct row; "
                f"had {len(opts)} option(s)"
            )

        rm = secrets.choice(removable)

        opts = opts[:rm] + opts[rm + 1 :]
        ci = [c - 1 if c > rm else c for c in ci if c != rm]
        if rm < keep_correct:
            keep_correct -= 1

    return opts, ci
