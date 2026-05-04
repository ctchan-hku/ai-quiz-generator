"""model_catalog: normalization, Poe price map, and GET /api/models catalog build."""

import json

import pytest

from app.helpers.model_catalog import (
    build_api_models_catalog,
    catalog_entry_has_explicit_price,
    estimate_usage_cost,
    load_poe_price_map,
    merge_reference_prices_into_catalog,
    normalize_model_entry,
)


def test_normalize_explicit_price() -> None:
    row = normalize_model_entry({"id": "x", "label": "X", "price": {"input": 1.0, "output": 2.0}})
    assert row["price"]["input"] == 1.0


def test_normalize_price_shape_matches_reference_file() -> None:
    row = normalize_model_entry(
        {"id": "a", "label": "A", "price": {"input": 1.5, "output": 3.0}},
    )
    assert row["price"]["input"] == 1.5
    assert row["price"]["output"] == 3.0


def test_explicit_price_blocks_merge() -> None:
    raw_env_entries = [{"id": "x", "label": "X", "price": {"input": 9.0, "output": None}}]
    normalized = [normalize_model_entry(dict(r)) for r in raw_env_entries]
    ref = {"x": {"input": 1.0, "output": 1.0}}
    merged = merge_reference_prices_into_catalog(normalized, raw_env_entries, ref)
    assert merged[0]["price"]["input"] == 9.0


def test_catalog_entry_has_explicit_false_when_price_absent() -> None:
    assert catalog_entry_has_explicit_price({"id": "z", "label": "Z"}) is False


def test_load_poe_price_map_reads_tmp_file(tmp_path) -> None:
    p = tmp_path / "poe_ai_models.json"
    p.write_text(
        json.dumps(
            {
                "models": [
                    {"id": "alpha", "price": {"input": 1.5, "output": 3.0}},
                    {"id": "beta", "price": {"input": None, "output": None}},
                ]
            }
        ),
        encoding="utf-8",
    )
    m = load_poe_price_map(p)
    assert m["alpha"]["input"] == pytest.approx(1.5)
    assert m["beta"]["output"] is None


def test_build_api_models_catalog_merges_from_ref(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    from unittest.mock import MagicMock

    p = tmp_path / "poe_ai_models.json"
    p.write_text(
        json.dumps({"models": [{"id": "m1", "price": {"input": 2.0, "output": 4.0}}]}),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "app.helpers.model_catalog.load_poe_price_map",
        lambda path=None: load_poe_price_map(p),
    )

    s = MagicMock()
    s.available_models_raw = json.dumps([{"id": "m1", "label": "One"}])
    cat = build_api_models_catalog(s)
    assert len(cat) == 1
    assert cat[0]["price"]["input"] == pytest.approx(2.0)


def test_estimate_usage_cost_matches_priced_input_and_output() -> None:
    catalog = [{"id": "m", "label": "M", "price": {"input": 1.0, "output": 2.0}}]
    assert estimate_usage_cost("m", 1_000_000, 500_000, catalog).cost_usd == 2.0


def test_estimate_usage_missing_output_price_counts_completion_at_zero() -> None:
    catalog = [{"id": "m", "label": "M", "price": {"input": 1.0, "output": None}}]
    assert estimate_usage_cost("m", 1_000_000, 500_000, catalog).cost_usd == pytest.approx(1.0)


def test_estimate_usage_missing_input_price_counts_prompt_at_zero() -> None:
    catalog = [{"id": "m", "label": "M", "price": {"input": None, "output": 2.0}}]
    assert estimate_usage_cost("m", 1_000_000, 500_000, catalog).cost_usd == pytest.approx(1.0)
