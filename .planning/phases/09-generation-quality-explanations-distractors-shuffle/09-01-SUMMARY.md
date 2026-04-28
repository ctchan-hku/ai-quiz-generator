---
phase: 09-generation-quality-explanations-distractors-shuffle
plan: 01
subsystem: api
tags: [fastapi, pydantic, prompts, mcq]

requires: []
provides:
  - Stronger MCQ instructions (stem, distractors, stepped explanations)
  - Topic vs few-shot user-message balance in FullQuizLlm
  - Cryptographic option shuffle after validate in full quiz + single MCQ parse
affects: [generate API consumers, UAT]

tech-stack:
  added: []
  patterns:
    - Post-parse shuffle preserves validation invariants; no shuffle in validators.

key-files:
  created: []
  modified:
    - backend/app/services/prompts.py
    - backend/app/helpers/options.py
    - backend/app/services/llm/full_quiz.py
    - backend/app/services/llm/single_mcq.py
    - backend/tests/test_helpers_options.py
    - README.md

key-decisions:
  - Shuffle via secrets.SystemRandom after model_validate, not in Pydantic validators.
  - User message frames topic as coverage; few-shot lines prioritized when present.

requirements-completed: []

duration: —
completed: "2026-04-28"
---

# Phase 9 — Plan 01 summary

**Backend now instructs models for reasoning-first stems, plausible distractors, numbered deduction explanations; reframes full-quiz user prompt for topic scope vs few-shot dominance; shuffles returned option order with remapped correct indices.**

## Performance

- **Tasks:** 4 completed (single implementation pass)
- **Verification:** `python -m pytest -q` → 46 passed · `npx tsc --noEmit` (frontend) → clean

## Accomplishments

- Extended `MULTIPLE_CHOICE_INSTRUCTIONS` and `REWRITE_HINT` with ordered workflow and stepped-explanation contract.
- Full-quiz user message describes coverage/direction, optional few-shot priority line when examples exist.
- `shuffle_option_order` in `options.py`; wired in `FullQuizLlm.parse` and `SingleMcqLlm.parse`.
- Unit tests for shuffle invariants + roundtrip; README notes stepped explanations and server shuffle.

## Files touched

| Area | Path |
|------|------|
| Prompts | `backend/app/services/prompts.py` |
| Shuffle helper | `backend/app/helpers/options.py` |
| LLM | `backend/app/services/llm/full_quiz.py`, `single_mcq.py` |
| Tests | `backend/tests/test_helpers_options.py` |
| Docs | `README.md` |

## Self-Check: PASSED

- Acceptance checks from plan re-run: grep language present in `prompts.py`; pytest + tsc as in `<verification>`.
