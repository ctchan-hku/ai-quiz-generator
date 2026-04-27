# Project State — AI Quiz Generator

**Last updated:** 2026-04-27  
**Updated by:** `/gsd-execute-phase 6` — phase 6 closed; current focus **phase 7**

---

## Project reference

**Core value:** Given a topic or document, produce a ready-to-use multiple-choice quiz in seconds — no account, no friction.

**Current focus:** **v1.1** — Few-shot examples in system prompt, **gpt-4.1** model option, per-question **refine** via **`POST /api/generate/question`** and optional **comment**.

**Stack:** FastAPI (Railway) + React/Vite (Vercel) + OpenAI-compatible API (openai-hk.com)

---

## Current position

| Field | Value |
|-------|-------|
| **Milestone** | v1.1 (generation quality & control) |
| **Current phase** | 7 — Per-question regeneration *(planned)* |
| **Current plan** | [07-01-PLAN.md](phases/07-regenerate-question/07-01-PLAN.md) → [07-02-PLAN.md](phases/07-regenerate-question/07-02-PLAN.md) |
| **Phase status** | 1/2 v1.1 phases delivered *(phase 6 complete)* |
| **Last action** | `/gsd-execute-phase 6` — verified `pytest` + `tsc`; roadmap/reqs updated |

**Progress:** `██████████░░░░░░░░░░` 50% (v1.1 — 1 of 2 phases)

---

## Phase summary (v1.1)

| # | Phase | Status |
|---|-------|--------|
| 6 | Few-shot examples + math model | **Complete** (2026-04-27) |
| 7 | Per-question regeneration | Planned |

*v1.0 phases 1–5: complete (see [milestones/v1.0-ROADMAP.md](milestones/v1.0-ROADMAP.md)).*

---

## Next action

1. **`/gsd-plan-phase 7`** (or **execute** when `07-*.PLAN.md` exist) — per-question regeneration API + review UI.  
2. Optional: run manual rows in [06-UAT.md](phases/06-few-shot-math-model/06-UAT.md) for **AI-FS-04** (with vs without few-shot spot-check) if not yet done.  
3. Optional: close PROJECT **Active** checklist item (public URL) if still open.

---

## Quick tasks completed

| Slug | Completed | Notes |
|------|-----------|--------|
| parser-unit-tests | 2026-04-23 | `backend/tests/test_parser.py` |
| railway-logs-dev-port | 2026-04-23 | Procfile log config; port 8080 |
| frontend-dev-remote-script | 2026-04-23 | `npm run dev:remote` |
| quiz-summary-actions-copy | 2026-04-27 | CurrentQuizActions copy |
| quiz-actions-beside-display | 2026-04-27 | QuizDisplay column layout |
| v1.0-milestone-archive | 2026-04-27 | `chore: archive v1.0 milestone`; tag `v1.0` |
| quiz-form-split | 2026-04-27 | `components/QuizForm/` — Topic, number, model, few-shot subcomponents + `index.ts` |
| llm-full-prompt-log | 2026-04-27 | `LOG_FULL_LLM_PROMPT` + `app/llm_debug_log.py` — opt-in full chat `messages` logging |

---

## Performance metrics (v1.0 baseline)

| Metric | Value |
|--------|-------|
| v1 requirements delivered | 24 |
| v1.1 requirements drafted | 18 checklist items (REQUIREMENTS.md) |
| v1.1 phases | 2 |
