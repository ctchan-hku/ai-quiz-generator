"""Calculate cost based on Poe model pricing JSON."""

import json
from functools import lru_cache
from pathlib import Path


@lru_cache(maxsize=1)
def _load_poe_pricing() -> dict[str, dict[str, str | None] | None]:
    pricing_path = Path(__file__).resolve().parents[4] / "data" / "poe_models_pricing.json"
    if not pricing_path.exists():
        return {}
    with open(pricing_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return {item["id"]: item["pricing"] for item in data}


def calculate_cost(model_id: str, usage: dict[str, int]) -> float:
    """Calculate the cost of a generation run based on Poe model pricing.

    Returns 0.0 if the model is not found or has no pricing.
    """
    pricing_data = _load_poe_pricing()
    model_pricing = pricing_data.get(model_id)
    if not model_pricing:
        return 0.0

    prompt_price_str = model_pricing.get("prompt")
    completion_price_str = model_pricing.get("completion")

    prompt_price = float(prompt_price_str) if prompt_price_str else 0.0
    completion_price = float(completion_price_str) if completion_price_str else 0.0

    prompt_tokens = usage.get("prompt_tokens", 0)
    completion_tokens = usage.get("completion_tokens", 0)

    return (prompt_tokens * prompt_price) + (completion_tokens * completion_price)
