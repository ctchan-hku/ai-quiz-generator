# Phase 9 — CONTEXT

**Status:** Shipped (2026-04-30) — backend prompts, topic/example balance (system + user task line), **server-side shuffle** after parse for full quiz and single MCQ. See [09-01-SUMMARY.md](09-01-SUMMARY.md).

## Goal

Raise **quiz quality** so that: (1) stems and keyed answers are **truth-consistent**; (2) explanations show **explicit reasoning / deduction steps**; (3) wrong options are **credibly distracting** relative to the stem; (4) answer positions are **not biased** toward a slot (e.g. index 0); (5) when users supply **topic + examples**, generation **balances** topic as broad direction against examples as **structure / domain / difficulty** anchors.

## Requirements

Formal IDs live in [.planning/REQUIREMENTS.md](../../REQUIREMENTS.md) (**AI-Q9-01** … **AI-Q9-03**).

## Depends on

- Phase 8 (instructions + quiz layout) — complete.

## Resolved decisions *(formerly open questions)*

1. **Shuffle:** **Server-side only** after successful Pydantic validation — **`shuffle_option_order`** in `app/helpers/options.py` using **`secrets.SystemRandom`**. The model is **not** asked to randomize option order; one consistent policy across full-quiz and refine flows.
2. **Explanation length:** Soft cap communicated in prompts (`MCQ_EXPLANATION_SOFT_MAX_CHARS`); no hard **`Field(max_length=…)`** on **`explanation`** in v1.1 — truncate oversized payloads later if telemetry shows abuse.
3. **Single vs second LLM pass:** **Single call** with **`MCQ_CHAIN_OF_THOUGHT`** ordering in the system prompt; no mandatory second pass for distractors-only in this milestone.

## References

- Prompts: `backend/app/services/prompts.py`
- Full-quiz messages: `backend/app/services/llm/full_quiz.py`
- Single MCQ: `backend/app/services/llm/single_mcq.py`
- Shuffle helper: `backend/app/helpers/options.py`
