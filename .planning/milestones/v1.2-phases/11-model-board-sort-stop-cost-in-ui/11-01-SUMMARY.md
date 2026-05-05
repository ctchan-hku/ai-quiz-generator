---
phase: 11-model-board-sort-stop-cost-in-ui
plan: "01"
subsystem: frontend
tags: [react, models, pricing, tanstack-query]

requires:
  - phase: 10
    provides: GET /api/models with price.input / price.output (USD per 1M tokens)
provides:
  - ModelInfo + ModelPrice typings aligned with backend catalog
  - ModelBoard (radiogroup, price asc/desc sort, card selection) replacing ModelField select
affects:
  - 11-02 (Stop, cost display in UI — unchanged by this wave)

tech-stack:
  added: []
  patterns:
    - "Comparable scalar sort via priceSortKey + stable label/id ties"

key-files:
  created:
    - frontend/src/components/QuizForm/ModelBoard.tsx
  modified:
    - frontend/src/types/api.ts
    - frontend/src/components/QuizForm/QuizForm.tsx
  removed:
    - frontend/src/components/QuizForm/ModelField.tsx

key-decisions:
  - "Sort uses sum of normalized input+output USD/M (unknown → Infinity so they sort last in ascending mode)"

patterns-established:
  - "fieldset + legend for group; role=radiogroup on card grid"

requirements-completed:
  - FE-MB-01
  - FE-MB-02
  - FE-MB-03

duration: unknown
completed: 2026-05-04
---

# Phase 11 — Plan 11-01 summary (Wave 1)

**Outcome:** The quiz form uses a **model board** populated from **`GET /api/models`**, showing **label**, **id**, **formatted USD/M input & output**, **Pricing unavailable** when both rates are null, and **Price: Low to high / High to low** sort controls. **`ModelField`** (`<select>`) is removed.

## Automated checks

- `cd frontend && npm run build` — passed
- `cd frontend && npm run lint` — passed

## Self-Check: PASSED

- **`ModelBoard`**, **`ModelPrice`**, **`grep ModelField`** over `frontend/src` — no matches

## Deviations

- None
