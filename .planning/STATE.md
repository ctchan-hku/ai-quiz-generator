# Project State — AI Quiz Generator

**Last updated:** 2026-04-27  
**Updated by:** `/gsd-new-milestone` — **v1.1** requirements + roadmap

---

## Project reference

**Core value:** Given a topic or document, produce a ready-to-use multiple-choice quiz in seconds — no account, no friction.

**Current focus:** **v1.1** — Few-shot examples in system prompt, **gpt-4.1** model option, per-question **regeneration** with user instruction.

**Stack:** FastAPI (Railway) + React/Vite (Vercel) + OpenAI-compatible API (openai-hk.com)

---

## Current position

| Field | Value |
|-------|-------|
| **Milestone** | v1.1 (generation quality & control) |
| **Current phase** | 6 — Few-shot + math model *(build done; UAT / commit)* |
| **Current plan** | `06-01-PLAN.md` ✓ `06-02-PLAN.md` ✓ — run `06-UAT.md` |
| **Phase status** | 0/2 v1.1 phases executed *(phase 6 code: waves 1–2 done)* |
| **Last action** | Phase 6 Wave 2 — QuizForm few-shot UI + `generateQuiz(QuizFormConfig)` |

**Progress:** `░░░░░░░░░░░░░░░░░░░░` 0% (v1.1)

---

## Phase summary (v1.1)

| # | Phase | Status |
|---|-------|--------|
| 6 | Few-shot examples + math model | Built — verify with `06-UAT.md` |
| 7 | Per-question regeneration | Planned |

*v1.0 phases 1–5: complete (see [milestones/v1.0-ROADMAP.md](milestones/v1.0-ROADMAP.md)).*

---

## Next action

1. **Phase 6** — Run [.planning/phases/06-few-shot-math-model/06-UAT.md](phases/06-few-shot-math-model/06-UAT.md); **close phase 6** when satisfied.  
2. **`/gsd-plan-phase 7`** — executable plans for regenerate endpoint + UI.  
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

---

## Performance metrics (v1.0 baseline)

| Metric | Value |
|--------|-------|
| v1 requirements delivered | 24 |
| v1.1 requirements drafted | 18 checklist items (REQUIREMENTS.md) |
| v1.1 phases | 2 |
