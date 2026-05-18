"""Fetch Poe GET /v1/models and write JSON: each model’s ``id`` and ``pricing``."""

import json
import os
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen


def main() -> None:
    backend_root = Path(__file__).resolve().parents[1]

    url = os.environ.get("POE_MODELS_JSON_URL", "https://api.poe.com/v1/models")
    path_raw = os.environ.get("POE_MODELS_PRICING_PATH")
    output_file = (
        Path(path_raw)
        if path_raw
        else backend_root / "data" / "poe_models_pricing.json"
    )

    req = Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "ai-quiz-generator-fetch-poe-models-pricing/1",
        },
        method="GET",
    )
    try:
        with urlopen(req, timeout=120) as resp:
            text = resp.read().decode("utf-8")
    except URLError as e:
        raise SystemExit(f"Poe models request failed: {e}") from e

    if text.lstrip().startswith("<"):
        raise SystemExit(
            "Poe endpoint returned HTML, not JSON. "
            "Set POE_MODELS_JSON_URL to https://api.poe.com/v1/models.",
        )

    decoded = json.loads(text)
    rows = [{"id": m["id"], "pricing": m["pricing"]} for m in decoded["data"]]

    output_file.parent.mkdir(parents=True, exist_ok=True)
    tmp = output_file.with_suffix(output_file.suffix + ".new")
    tmp.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    tmp.replace(output_file)
    print(output_file.resolve())


if __name__ == "__main__":
    main()
