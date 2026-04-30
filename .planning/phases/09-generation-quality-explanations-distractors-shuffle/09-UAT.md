---
status: complete
updated: 2026-04-30
---

# Phase 9 — UAT checklist

**Phase:** Reasoning-first MCQs, stepped explanations, distractors & shuffle  
**Shipped:** 2026-04-30

## Automated verification

| Check | Command | Result |
|--------|---------|--------|
| Backend unit tests | `cd backend && python -m pytest tests/ -q` | **54 passed** |
| Shuffle remap | `test_helpers_options.py` (`test_full_quiz_parse_remaps_correct_indices_after_shuffle`) | **Pass** |
| Prompt contract | `prompts.py` — stepped explanation + chain-of-thought order | **Static review** |

## Manual / subjective

- Spot-check generated quizzes for **numbered explanation steps** and plausible distractors (model-dependent).
- Confirm UI export/copy still matches **selected** versions after option shuffle (labels **A–D** follow new order).

## Outcome

**Signed off 2026-04-30** — backend contract enforced; qualitative quality remains provider/model dependent.
