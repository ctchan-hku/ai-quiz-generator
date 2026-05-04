"""Unit tests for `estimate_usage_cost_usd` (Phase 10)."""

import pytest

from app.helpers.model_catalog import estimate_usage_cost_usd


def test_estimate_usage_cost_matches_priced_input_and_output() -> None:
    catalog = [
        {"id": "m", "label": "M", "price": {"input": 1.0, "output": 2.0}},
    ]
    assert (
        estimate_usage_cost_usd("m", 1_000_000, 500_000, catalog) == 2.0
    )


def test_missing_output_price_counts_completion_at_zero() -> None:
    catalog = [
        {"id": "m", "label": "M", "price": {"input": 1.0, "output": None}},
    ]
    assert estimate_usage_cost_usd("m", 1_000_000, 500_000, catalog) == pytest.approx(1.0)


def test_missing_input_price_counts_prompt_at_zero() -> None:
    catalog = [
        {"id": "m", "label": "M", "price": {"input": None, "output": 2.0}},
    ]
    assert estimate_usage_cost_usd("m", 1_000_000, 500_000, catalog) == pytest.approx(1.0)
