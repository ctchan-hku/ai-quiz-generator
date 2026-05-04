---
phase: 10-models-api-pricing-generate-cost-fields
plan: "02"
subsystem: api
tags: [openai, usage, cost_usd, generate]

requires:
  - plan: 10-01
    provides: Normalized model catalog prices on `settings.available_models`
provides:
  - `TokenUsage` + `add_usage`; `complete_chat` returns usage from first completion
  - `parse_llm_with_retry` returns `(T, TokenUsage)` and merges retry completion usage
  - `estimate_usage_cost_usd` / `lookup_model_price` in `model_catalog`
  - `QuizResponse.cost_usd`; `QuestionGenerateResponse` for `POST /api/generate/question`
  - Frontend unwraps `question` + types `cost_usd` on quiz responses
affects:
  - Phase 11 UI for displaying costs

tech-stack:
  added: []
  patterns:
    - "Routers compute `cost_usd` from aggregated `TokenUsage` and `settings.available_models` rates"

key-files:
  created:
    - backend/app/models/usage.py
    - backend/tests/test_usage_cost.py
    - backend/tests/test_generate_cost_fields.py
    - backend/tests/test_generate_quiz_request.py
    - backend/tests/test_generate_question_messages.py
  modified:
    - backend/app/helpers/model_catalog.py
    - backend/app/services/llm/openai/client.py
    - backend/app/services/parser.py
    - backend/app/services/llm/core/bases.py
    - backend/app/services/llm/core/protocols.py
    - backend/app/models/schemas.py
    - backend/app/routers/generate.py
    - backend/tests/services/test_parser.py
    - frontend/src/lib/api.ts
    - frontend/src/types/quiz.ts
    - frontend/src/types/quiz-machine.ts
    - README.md

key-decisions:
  - "Question endpoint uses wrapper JSON `{ question, cost_usd }`; client continues to receive `MultipleChoiceQuestion` via `data.question`"

requirements-completed:
  - API-COST-01
  - API-COST-02

duration: unknown
completed: 2026-05-04
---

# Phase 10 — Plan 10-02 summary (Wave 2)

**Outcome:** Successful **`POST /api/generate/quiz`** and **`POST /api/generate/question`** responses include **`cost_usd`**, computed from provider-reported **`usage`** and per-model **`price.input` / `price.output`** (USD per 1M tokens) on **`settings.available_models`**. Retry parses accumulate tokens from the corrective completion.

## Verification

- `pytest backend/tests` — **73 passed** (2026-05-04).

## Self-Check: PASSED

- `compileall` clean; no bare **`response_model=MultipleChoiceQuestion`** on generate router.
