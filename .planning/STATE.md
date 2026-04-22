# Project State — AI Quiz Generator MVP

**Last updated:** 2026-04-22
**Updated by:** planning docs — discriminated union schema

---

## Project Reference

**Core value:** Given a topic or document, produce a ready-to-use multiple-choice quiz in seconds — no account, no friction.

**Current focus:** Phase 1 — Backend Scaffold

**Stack:** FastAPI (Railway) + React/Vite (Vercel) + openai-hk.com API

---

## Current Position

| Field | Value |
|-------|-------|
| **Current phase** | Phase 1: Backend Scaffold |
| **Current plan** | Not started |
| **Phase status** | Not started |
| **Last action** | Roadmap created |

**Progress:** `░░░░░░░░░░░░░░░░░░░░` 0% (0/7 phases complete)

---

## Phase Summary

| # | Phase | Status |
|---|-------|--------|
| 1 | Backend Scaffold | Not started |
| 2 | AI Generation Pipeline | Not started |
| 3 | React Frontend — Topic Flow | Not started |
| 4 | File Upload Backend | Not started |
| 5 | File Upload Frontend | Not started |
| 6 | Export | Not started |
| 7 | Model Selection UI | Not started |

---

## Accumulated Context

### Locked Decisions

| Decision | Rationale |
|----------|-----------|
| Discriminated union on `question_type` | Narrow types; no invalid combinations of options/indices/expected_answer |
| `QuestionBase` + `OptionsQuestion` + four variant classes | Shared fields on bases; TF/MCQ/multi-select share options branch; `ShortAnswerQuestion` has `expected_answer` only |
| `correct_indices: list[int]` on options variants | MCQ/TF: one index; multi-select: multiple indices — validators per class |
| v1 LLM emits only `multiple_choice` | Other union members exist for API/tests; generation + UI renderers added in v2 |
| `files: list[UploadFile]` on backend | Adding multi-file is a pure frontend change; backend already handles the list |
| `extra_context` optional field on `/generate/file` | Combines typed notes + uploaded document without a new endpoint |
| Two generate endpoints (`/text` + `/file`) | Browsers cannot mix JSON and multipart in one request |
| Hardcoded model list in env var | Live `/v1/models` fetch risks key exposure and adds startup dependency |
| Rate limiting in Phase 2 (before public URL) | Anonymous app has no billing firewall; 3 req/IP/hour via `slowapi` |
| pypdf only for PDF extraction (no pdfplumber) | Zero native deps; add pdfplumber in v1.1 if multi-column complaints emerge |
| Scanned PDF guard: < 50 words → reject | Silent empty extraction produces hallucinated quizzes — trust-destroying |
| 12,000-char truncation limit | ~3,000 tokens; chunking/sampling is post-MVP |
| `explanation` field included in v1 schema | Already in Pydantic schema and system prompt; negligible cost |
| React 19 + Vite + Tailwind v4 + shadcn/ui | Lightweight SPA for split-deploy; no SSR needed |
| `useReducer` state machine | Five explicit states; prevents impossible UI states |
| TanStack Query `useMutation` for generate flow | Correct primitive for generate→review async mutation |

### Critical Pitfalls to Avoid

1. **LLM JSON validation** — Always wrap in `try/except`; validate with Pydantic; one corrective retry; strip markdown fences
2. **Scanned PDF guard** — Check word count after extraction; reject < 50 words on multi-page PDF
3. **Rate limiting before public URL** — `slowapi` 3 req/IP/hour deployed in Phase 2
4. **CORS in production** — Load `ALLOWED_ORIGINS` from env; add `CORSMiddleware` first; test against Vercel URL
5. **Railway cold start** — `/health` endpoint + UptimeRobot ping every 5 min; stepped loading in frontend

### Open Questions (Resolved)

| Question | Resolution |
|----------|------------|
| Which models in dropdown? | Hardcoded list in `AVAILABLE_MODELS` env var |
| Rate limit threshold? | 3 req/IP/hour (conservative; adjust after real usage) |
| PDF size limit? | Both: 10MB upload cap + 30-page rejection |
| Include `explanation` field? | Yes — already in schema, negligible cost |
| Rate limiting timing? | Phase 2 — endpoint is public on Railway deploy |
| Multi-column PDF handling? | pypdf only for MVP — warn user if output looks garbled |

### Todos

*(None yet)*

### Blockers

*(None)*

---

## Session Continuity

**How to resume:**

1. Read this STATE.md for current position
2. Read `.planning/ROADMAP.md` for phase goals and requirements
3. Check current phase's PLAN.md (if exists) in `.planning/phases/phase-N/`
4. Run `/gsd-progress` to get a full status report

**Next action:** `/gsd-plan-phase 1` — plan Phase 1: Backend Scaffold

---

## Performance Metrics

| Metric | Value |
|--------|-------|
| Total requirements | 30 |
| Requirements mapped | 30 |
| Phases planned | 7 |
| Phases complete | 0 |
| Plans written | 0 |
| Plans complete | 0 |
