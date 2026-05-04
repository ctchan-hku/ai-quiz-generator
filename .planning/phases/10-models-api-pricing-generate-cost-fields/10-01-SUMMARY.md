---
phase: 10-models-api-pricing-generate-cost-fields
plan: "01"
subsystem: api
tags: [fastapi, models, pricing, catalog, AVAILABLE_MODELS]

requires:
  - phase: v1.1
    provides: Shipped app and allowlisted models pattern
provides:
  - `normalize_model_entry` + `build_api_models_catalog` merging env allowlist with `backend/data/poe_ai_models.json`
  - `GET /api/models` returns `price.input` / `price.output` (USD per 1M tokens) per model row
  - `Settings.available_models` parses and normalizes `AVAILABLE_MODELS` JSON
affects:
  - 10-02 (cost_usd on generate endpoints)

tech-stack:
  added: []
  patterns:
    - "Pre-built `app.state.models_catalog` in FastAPI lifespan from `build_api_models_catalog(settings)`"

key-files:
  created:
    - backend/app/helpers/model_catalog.py
    - backend/tests/helpers/test_model_catalog.py
  modified:
    - backend/app/config.py
    - backend/app/main.py
    - README.md

key-decisions:
  - "Explicit `price` on an env row blocks overwrite by reference JSON; missing price merges from `poe_ai_models.json` when ids match"

patterns-established:
  - "Router reads `request.app.state.models_catalog` with fallback to `settings.available_models`"

requirements-completed:
  - MOD-03
  - MOD-04

duration: unknown
completed: 2026-04-30
---

# Phase 10 — Plan 10-01 summary (Wave 1)

**Outcome:** The backend exposes a stable **`price`** object on each **`GET /api/models`** entry, sourced from **`AVAILABLE_MODELS`** and merged with **`backend/data/poe_ai_models.json`** where configured, without changing existing **`id`** / **`label`** consumers.

## Performance

- **Tasks (plan):** 3 (catalog helper, config wiring + docs, tests)
- **Primary commit:** `70114b6` — feat: add model catalog helper with price normalization

## Accomplishments

- Added **`model_catalog`** module: normalization, Poe price map load, merge into API-shaped rows.
- **`Settings.available_models`** normalizes parsed JSON; **`main`** lifespan builds **`models_catalog`** once at startup.
- **`README.md`** documents **`AVAILABLE_MODELS`** / **`price`** semantics and reference JSON regeneration.

## Automated checks

- `pytest backend/tests/helpers/test_model_catalog.py` — **6 passed** (2026-05-04).

## Self-Check: PASSED

- Key files from **`70114b6`** present; catalog tests green.
