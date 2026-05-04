---
status: testing
phase: 11-model-board-sort-stop-cost-in-ui
source:
  - 11-01-SUMMARY.md
  - 11-02-SUMMARY.md
started: "2026-05-04T12:00:00Z"
updated: "2026-05-04T12:00:00Z"
---

## Current Test

number: 1
name: Model board shows models with formatted pricing
expected: |
  On the quiz form, the model chooser is a board of cards (not a plain dropdown). Each card shows label, id, formatted USD/M for input and output, or a clear "Pricing unavailable" (or equivalent) when both rates are missing.
awaiting: paused until Phase 10 UAT completes (or user requests start Phase 11)

## Tests

### 1. Model board shows models with formatted pricing
expected: Card grid with label, id, formatted $/M input & output, or pricing-unavailable state when both null.
result: [pending]

### 2. Model board price sort
expected: Price sort controls (e.g. Low to high / High to low) reorder cards by comparable price; models with unknown pricing sort last in ascending mode.
result: [pending]

### 3. Stop during full-quiz generation
expected: While a full quiz is generating, Stop is available; aborting does not leave the app in a generic error state (user cancel should not look like a server failure). User can run Generate again.
result: [pending]

### 4. Stop during question refinement
expected: While refining a question, Stop cancels without showing a refine error attributed to user cancel.
result: [pending]

### 5. Estimated cost visible on review
expected: After a successful generate, the review view shows estimated USD cost (e.g. header or summary) for that run.
result: [pending]

### 6. Cost in clipboard and journal
expected: Copied export/summary text includes an estimated cost line; journal sidebar lists saved quizzes with cost where applicable (schema v2).
result: [pending]

## Summary

total: 6
passed: 0
issues: 0
pending: 6
skipped: 0
blocked: 0

## Gaps

<!-- Populated when a test is marked issue -->
