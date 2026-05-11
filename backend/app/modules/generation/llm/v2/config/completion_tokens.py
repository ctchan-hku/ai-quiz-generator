"""Completion ``max_tokens`` budgets for v2 pipeline steps (shared formula)."""

from app.modules.generation.services.prompter import MAX_COMPLETION_TOKENS

ANSWER_STEP_BASE_TOKENS = 400
ANSWER_STEP_PER_QUESTION_TOKENS = 500

DISTRACTOR_STEP_BASE_TOKENS = 400
DISTRACTOR_STEP_PER_QUESTION_TOKENS = 420


def completion_max_tokens_for_items(
    base_tokens: int,
    per_item_tokens: int,
    num_items: int,
) -> int:
    return min(MAX_COMPLETION_TOKENS, base_tokens + per_item_tokens * num_items)
