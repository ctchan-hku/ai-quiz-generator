from dataclasses import dataclass

from app.integrations.langchain.config import MAX_COMPLETION_TOKENS


@dataclass(frozen=True)
class CompletionTokenBudget:
    base_tokens: int
    per_item_tokens: int
    minimum_total: int | None = None

    def max_tokens(self, num_items: int) -> int:
        total = self.base_tokens + self.per_item_tokens * num_items
        if self.minimum_total is not None:
            total = max(total, self.minimum_total)
        return min(MAX_COMPLETION_TOKENS, total)


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
DIFFICULTY_TARGET_TOKEN_BUDGET = CompletionTokenBudget(
    base_tokens=128,
    per_item_tokens=32,
    minimum_total=256,
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
