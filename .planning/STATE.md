# Project State — AI Quiz Generator MVP

**Last updated:** 2026-04-24
**Updated by:** EXP-03 added (comments + `localStorage` export journal); `05-CONTEXT.md` + `REQUIREMENTS` / `ROADMAP` aligned

---

## Project Reference

**Core value:** Given a topic or document, produce a ready-to-use multiple-choice quiz in seconds — no account, no friction.

**Current focus:** Phase 5 — Export

**Stack:** FastAPI (Railway) + React/Vite (Vercel) + openai-hk.com API

---

## Current Position

| Field | Value |
|-------|-------|
| **Current phase** | Phase 5: Export (not started) |
| **Current plan** | — |
| **Phase status** | Phases 1–4 complete; **Phase 5 (Export)** remaining (`EXP-01` / `EXP-02`; upload deferred to v2) |
| **Last action** | Phase 5 discuss-phase: export implementation decisions captured in `05-export/05-CONTEXT.md` |

**Progress:** `████████████████░░░░` 80% (4/5 phases complete)

---

## Phase Summary

| # | Phase | Status |
|---|-------|--------|
| 1 | Backend Scaffold | Complete |
| 2 | AI Generation Pipeline | Complete |
| 3 | React Frontend — Topic Flow | Complete |
| 4 | Model Selection UI | Complete |
| 5 | Export | Not started |

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
| `POST /api/debug/chat-completion` in Phase 1 | Gated by `ENABLE_DEBUG_CHAT_COMPLETION`; real LLM smoke test; low `max_tokens`; disable on public prod unless intentional |
| pypdf only for PDF extraction (no pdfplumber) | Zero native deps; add pdfplumber in v1.1 if multi-column complaints emerge |
| Scanned PDF guard: < 50 words → reject | Silent empty extraction produces hallucinated quizzes — trust-destroying |
| 12,000-char truncation limit | ~3,000 tokens; chunking/sampling is post-MVP |
| `explanation` field included in v1 schema | Already in Pydantic schema and system prompt; negligible cost |
| React 19 + Vite + Tailwind v4 + shadcn/ui | Lightweight SPA for split-deploy; no SSR needed |
| `useReducer` state machine | Five explicit states; prevents impossible UI states |
| TanStack Query `useMutation` for generate flow | Correct primitive for generate→review async mutation |
| Question count UI **0–10** (± in `QuizForm`) | Matches backend `GenerateTextRequest`; not 5/10/15/20 (option A, 2026-04-24) |
| **Phase 4 = Model Selection**, **Phase 5 = Export** in `ROADMAP.md` | Matches user flow (configure → generate → review → export) and build order; Export lists **Depends on** Phase 3, Phase 4 |

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

**Next action:** `/gsd-plan-phase 5` (or manual planning from `05-CONTEXT.md`), then implement Export. Document upload is deferred — see `REQUIREMENTS.md` v2.

---

## Quick Tasks Completed

| Slug | Completed | Notes |
|------|-----------|--------|
| parser-unit-tests | 2026-04-23 | `backend/tests/test_parser.py`; run `pytest tests/test_parser.py` from `backend/` |
| railway-logs-dev-port | 2026-04-23 | Procfile `--log-config` stdout for Railway `level:info`; local dev port 8080 + Vite proxy |
| frontend-dev-remote-script | 2026-04-23 | `npm run dev:remote` + `frontend/.env.remote` for Railway dev API; `dev:local` alias |

---

## Performance Metrics

| Metric | Value |
|--------|-------|
| Total requirements (v1 active) | 23 |
| Requirements mapped (v1 roadmap) | 23 |
| Deferred (upload track, v2) | 9 |
| Phases planned | 5 |
| Phases complete | 4 |
| Plans written | 3 |
| Plans complete | — |