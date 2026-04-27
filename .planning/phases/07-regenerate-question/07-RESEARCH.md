# Phase 7 — Per-question regeneration (research)

**Date:** 2026-04-27  
**Mode:** Light — `07-CONTEXT.md` is authoritative; this file captures external constraints only.

## slowapi — shared quota (AI-RG-04, D-7-10)

- `slowapi` **0.1.9** (see `backend/requirements.txt`) exposes `Limiter.shared_limit(limit_value, scope, ...)` so multiple routes share one counter; `scope` replaces the per-endpoint id in the storage key.
- **Plan:** apply `@limiter.shared_limit("3/hour", scope="openai_generate_quota")` to **both** `POST /api/generate/text` and **`POST /api/generate/question`** (and **remove** the plain `@limiter.limit` on `generate_text` to avoid double-counting).
- **Verify:** 4th request within an hour to **either** route returns 429 (same client IP) when rate limiting is enabled.

## Single-object JSON + Pydantic (D-7-06)

- Full-quiz path expects `{ "questions": [...] }` and `parse_with_retry` normalizes a bare array. Regen path must validate a **single** `MultipleChoiceQuestion` object (no `questions` wrapper).
- **Plan:** new `parse_single_mcq_with_retry` in `parser.py` with corrective prompt referring to one MCQ object only; system prompt for regen must demand **one** JSON object matching the MCQ schema.

## References

- `.planning/phases/07-regenerate-question/07-CONTEXT.md`
- `backend/app/routers/generate.py`, `backend/app/services/parser.py`, `backend/app/services/llm.py`
