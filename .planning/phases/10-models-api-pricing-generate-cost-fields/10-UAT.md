---
status: testing
phase: 10-models-api-pricing-generate-cost-fields
source:
  - 10-01-SUMMARY.md
  - 10-02-SUMMARY.md
started: "2026-05-04T12:00:00Z"
updated: "2026-05-04T12:00:00Z"
---

## Current Test

number: 1
name: GET /api/models includes per-model pricing
expected: |
  Open DevTools → Network, load the app (or call GET /api/models). Each model object in the JSON includes `price` with `input` and `output` (numbers or null), in USD per 1M tokens, aligned with the shipped catalog contract.
awaiting: user response

## Tests

### 1. GET /api/models includes per-model pricing
expected: Each model entry includes price.input and price.output (numbers or null). Observable via Network tab on GET .../api/models or equivalent.
result: [pending]

### 2. Full quiz generate returns estimated cost
expected: Successful POST /api/generate/quiz response JSON includes cost_usd (number ≥ 0). Observable in Network tab (and in UI if surfaced in a later phase).
result: [pending]

### 3. Single question refine returns estimated cost
expected: Successful POST /api/generate/question response JSON includes cost_usd on the envelope plus the question payload. Observable in Network tab (and in UI if surfaced).
result: [pending]

## Summary

total: 3
passed: 0
issues: 0
pending: 3
skipped: 0
blocked: 0

## Gaps

<!-- Populated when a test is marked issue -->
