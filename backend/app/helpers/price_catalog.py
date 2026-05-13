"""AVAILABLE_MODELS normalization and merge with Poe reference prices by model id."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.helpers.json_file import read_json

_POE_JSON = Path(__file__).resolve().parents[2] / "data" / "poe_ai_models.json"


def load_poe_price_map(path: Path | None = None) -> dict[str, dict[str, float | None]]:
    data = read_json(path or _POE_JSON)
    if not isinstance(data, dict):
        return {}
    models = data.get("models")
    if not isinstance(models, list):
        return {}
    return {
        m["id"]: {"input": m["price"]["input"], "output": m["price"]["output"]}
        for m in models
    }


def catalog_entry_has_explicit_price(raw_entry: dict[str, Any]) -> bool:
    p = raw_entry.get("price")
    return isinstance(p, dict) and (
        p.get("input") is not None or p.get("output") is not None
    )


def normalize_model_entry(raw_entry: dict[str, Any]) -> dict[str, Any]:
    mid = raw_entry["id"]
    label = raw_entry.get("label") or mid
    p = raw_entry.get("price")
    if isinstance(p, dict):
        price = {"input": p.get("input"), "output": p.get("output")}
    else:
        price = {"input": None, "output": None}
    return {"id": mid, "label": label, "price": price}


def merge_reference_prices_into_catalog(
    normalized_models: list[dict[str, Any]],
    raw_env_entries: list[dict[str, Any]],
    ref_prices_by_id: dict[str, dict[str, float | None]],
) -> list[dict[str, Any]]:
    skip_merge_ids = {
        r["id"] for r in raw_env_entries if catalog_entry_has_explicit_price(r)
    }
    out: list[dict[str, Any]] = []
    for m in normalized_models:
        row = dict(m)
        iid = row["id"]
        if iid not in skip_merge_ids and iid in ref_prices_by_id:
            row["price"] = dict(ref_prices_by_id[iid])
        out.append(row)
    return out


def build_api_models_catalog(settings: Any) -> list[dict[str, Any]]:
    raw_env_entries: list[dict[str, Any]] = json.loads(settings.available_models_raw)
    normalized = [normalize_model_entry(dict(r)) for r in raw_env_entries]
    return merge_reference_prices_into_catalog(
        normalized, raw_env_entries, load_poe_price_map()
    )


def lookup_model_price(
    model_id: str, catalog: list[dict[str, Any]]
) -> tuple[float | None, float | None]:
    for row in catalog:
        if row.get("id") != model_id:
            continue
        p = row.get("price")
        if not isinstance(p, dict):
            return (None, None)
        return (p.get("input"), p.get("output"))
    return (None, None)


def estimate_usage_cost(
    model_id: str,
    prompt_tokens: int,
    completion_tokens: int,
    catalog: list[dict[str, Any]],
    *,
    log_route: str | None = None,
) -> float:
    pt = max(0, int(prompt_tokens))
    ct = max(0, int(completion_tokens))
    p_in, p_out = lookup_model_price(model_id, catalog)
    rate_in = 0.0 if p_in is None else float(p_in)
    rate_out = 0.0 if p_out is None else float(p_out)
    total = (pt / 1_000_000) * rate_in + (ct / 1_000_000) * rate_out
    if log_route is not None:
        from app.modules.generation.helpers.logging import log_generate_usage

        log_generate_usage(
            route=log_route,
            model_id=model_id,
            prompt_tokens=pt,
            completion_tokens=ct,
            cost_usd=total,
            rate_input_per_million=p_in,
            rate_output_per_million=p_out,
        )
    return total
