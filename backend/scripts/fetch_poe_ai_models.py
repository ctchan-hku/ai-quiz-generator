#!/usr/bin/env python3
"""Fetch Poe GET /v1/models and write id + price (USD per million tokens).

Poe exposes pricing.prompt and pricing.completion as USD per token strings.
input/output USD/M = float(value) * 1e6.

Example (repo root):

  python backend/scripts/fetch_poe_ai_models.py --output backend/data/poe_ai_models.json

Uses OPENAI_API_KEY or POE_API_KEY as Bearer token when set (recommended).
OPENAI_BASE_URL defaults to https://api.poe.com/v1 when unset.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path


def token_usd_per_m(value: object) -> float | None:
    if value is None:
        return None
    try:
        return round(float(str(value)) * 1_000_000, 10)
    except (TypeError, ValueError):
        return None


def model_row(record: dict[str, object]) -> dict[str, object]:
    pricing = record.get("pricing")
    inp = out_val = None
    if isinstance(pricing, dict):
        inp = token_usd_per_m(pricing.get("prompt"))
        out_val = token_usd_per_m(pricing.get("completion"))
    return {
        "id": record["id"],
        "price": {"input": inp, "output": out_val},
    }


def fetch_models(base_url: str, api_key: str | None) -> dict[str, object]:
    url = f"{base_url.rstrip('/')}/models"
    headers = {"User-Agent": "mastery-exec/fetch-poe-ai-models"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            body = resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        hint = ""
        if e.code == 401:
            hint = " Set OPENAI_API_KEY or POE_API_KEY if Poe requires auth."
        raise SystemExit(f"HTTP {e.code} from {url}.{hint}") from e
    except urllib.error.URLError as e:
        raise SystemExit(f"Request failed: {e}") from e
    return json.loads(body)


def main() -> None:
    default_out = Path(__file__).resolve().parent.parent / "data" / "poe_ai_models.json"
    p = argparse.ArgumentParser(description="Generate poe_ai_models.json from Poe /v1/models.")
    p.add_argument(
        "--output",
        "-o",
        type=Path,
        default=default_out,
        help=f"JSON output path (default: {default_out})",
    )
    p.add_argument(
        "--base-url",
        default=os.environ.get("OPENAI_BASE_URL", "https://api.poe.com/v1"),
        help="API base URL including /v1",
    )
    args = p.parse_args()

    api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("POE_API_KEY")

    payload = fetch_models(args.base_url, api_key)
    rows = payload.get("data")
    if not isinstance(rows, list):
        raise SystemExit("Unexpected API shape: missing list data")

    models_list = [model_row(m) for m in rows]
    doc = {"models": models_list}

    out_path: Path = args.output
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    print(
        f"Wrote {len(models_list)} models to {out_path} "
        f"(from {args.base_url.rstrip('/')}/models)",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
