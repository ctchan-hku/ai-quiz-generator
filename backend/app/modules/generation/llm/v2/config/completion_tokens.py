"""Completion ``max_tokens`` budgets for v2 pipeline steps (shared formula)."""

from dataclasses import dataclass

from app.modules.generation.services.prompter import MAX_COMPLETION_TOKENS


@dataclass(frozen=True)
class CompletionTokenBudget:
    """Linear budget: ``base_tokens + per_item_tokens * num_items``, capped globally.

    When ``minimum_total`` is set, the linear sum is floored before the global cap
    (used for stem JSON so single-question runs are not squeezed).
    """

    base_tokens: int
    per_item_tokens: int
    minimum_total: int | None = None


QUESTION_STEM_STEP_TOKEN_BUDGET = CompletionTokenBudget(
    base_tokens=512,
    per_item_tokens=280,
    minimum_total=2048,
)
INSTRUCTION_ROUTER_TOKEN_BUDGET = CompletionTokenBudget(
    base_tokens=640,
    per_item_tokens=140,
    minimum_total=1024,
)
ANSWER_STEP_TOKEN_BUDGET = CompletionTokenBudget(
    base_tokens=512,
    per_item_tokens=880,
    minimum_total=3072,
)
DISTRACTOR_STEP_TOKEN_BUDGET = CompletionTokenBudget(
    base_tokens=512,
    per_item_tokens=560,
    minimum_total=2048,
)


def completion_max_tokens_for_items(budget: CompletionTokenBudget, num_items: int) -> int:
    total = budget.base_tokens + budget.per_item_tokens * num_items
    if budget.minimum_total is not None:
        total = max(total, budget.minimum_total)
    return min(MAX_COMPLETION_TOKENS, total)
