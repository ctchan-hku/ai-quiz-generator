import json
from functools import lru_cache

from app.config import settings
from app.integrations.langchain.token_usage import TokenUsage


@lru_cache(maxsize=1)
def _load_poe_pricing() -> dict[str, dict[str, str | None] | None]:
    pricing_path = settings.poe_models_pricing_path
    if not pricing_path.exists():
        return {}
    with open(pricing_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return {item["id"]: item["pricing"] for item in data}


def calculate_cost(model_id: str, usage: TokenUsage) -> float:
    pricing_data = _load_poe_pricing()
    model_pricing = pricing_data.get(model_id)
    if not model_pricing:
        return 0.0

    prompt_price_str = model_pricing.get("prompt")
    completion_price_str = model_pricing.get("completion")

    prompt_price = float(prompt_price_str) if prompt_price_str else 0.0
    completion_price = float(completion_price_str) if completion_price_str else 0.0

    return (usage.prompt_tokens * prompt_price) + (
        usage.completion_tokens * completion_price
    )
