# AI Quiz Generator MVP

## Current state (milestone)

- **v1.0** is **shipped & archived** (tag `v1.0`): topic-only MCQ, model UI, export + journal.
- **v1.1** is **active in planning**: few-shot / style examples in the system prompt, **gpt-4.1** in the model catalog (math/reasoning), **per-question regeneration** with optional user instruction.
- Snapshots: [.planning/milestones/v1.0-ROADMAP.md](milestones/v1.0-ROADMAP.md), [.planning/milestones/v1.0-REQUIREMENTS.md](milestones/v1.0-REQUIREMENTS.md).

## Next milestone goals (v1.1)

- **Phase 6** — ✓ *Shipped 2026-04-27* — few-shot on generate, **gpt-4.1** in catalog, docs, QuizForm UI.
- **Phase 7** — Regenerate single question API + review UI + state update. Next: **`/gsd-plan-phase 7`** or execute 07 plans.

## What This Is

A web application that lets anyone generate multiple-choice quizzes from a topic prompt (document upload planned for v2). The Python backend calls the OpenAI API to produce questions, and users can export the generated quiz. The app is publicly hosted with no login required — ship a link and anyone can try it.

## Core Value

Given a topic or document, produce a ready-to-use multiple-choice quiz in seconds — no account, no friction.

## Requirements

### Validated

- **Phase 1 (Backend Scaffold)** — FastAPI + CORS; `GET /health`, `GET /api/models`; gated `POST /api/debug/chat-completion`; Railway deploy with env-based config (no secrets in code). *Validated 2026-04-22 via UAT (`01-UAT.md`).*
- **Phases 2–5 (v1 topic MVP)** — Topic generation, review, model selection, **export**: plain-text clipboard + JSON journal (`localStorage`) with optional per-question comments (`EXP-01`–`EXP-03`). *Shipped 2026-04-24.*
- **Phase 6 (v1.1)** — Optional **few-shot / style examples** in the system prompt, **`gpt-4.1`** in the model list, FE `QuizForm` + API types. *Delivered 2026-04-27* (`06-01` / `06-02` plans; verify manual UAT rows in `06-UAT.md` for **AI-FS-04** as needed).*

### Active

- [ ] App is publicly accessible via a URL on Railway/Render with no login required *(verify ongoing deploy)*

### Out of Scope

- Document upload (text/PDF) for quiz generation — deferred to next milestone; v1.0 is topic-only (see archived requirements)
- User accounts / authentication — MVP is anonymous; saves complexity for v1
- True/False, short-answer, fill-in-the-blank questions — multiple choice only for MVP focus
- Quiz scoring / response collection — generation only, not proctoring
- Custom branding / themes — plain functional UI for MVP
- Manual **editing** of question text in the UI — still out of scope; **v1.1** adds **AI regeneration** per question with a prompt, not a full editor

## Context

- **Reference product**: Jotform AI Quiz Generator (https://www.jotform.com/ai/quiz-generator/) — the UX pattern to replicate at MVP scale
- **AI API**: OpenAI-compatible endpoint at https://api.openai-hk.com (drop-in for openai Python SDK; base URL: `https://api.openai-hk.com/v1`)
- **Stack**: Python (FastAPI) backend + React (Vite) frontend, deployed on Railway (backend) + Vercel (frontend)
- **Target users**: Teachers, trainers, students, trivia enthusiasts — anyone who needs a quiz fast

## Constraints

- **Tech stack**: Python backend (FastAPI), React frontend — decided during initialization
- **AI provider**: openai-hk.com OpenAI-compatible API — backend calls this endpoint for question generation
- **Auth**: None — fully anonymous, no session management required
- **Deployment**: Must produce a publicly shareable URL; Railway (backend) + Vercel (frontend) chosen
- **MVP scope**: Multiple choice only, no persistence, no user management
- **API schema**: Quiz questions use a Pydantic/TS discriminated union (`QuestionBase` → `OptionsQuestion` variants + `ShortAnswerQuestion`); v1 only generates `multiple_choice`

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| FastAPI over Flask | Async, auto-docs, cleaner typed API, better for AI streaming | Shipped (Phase 1) |
| React (Vite) over Next.js | Simpler deployment split; backend is pure API, frontend is pure UI | Shipped (v1.0) |
| No auth | MVP goal is demos and sharing; auth adds friction and time | Shipped (v1.0) |
| openai-hk.com API | Specified by user — drop-in OpenAI-compatible endpoint | Shipped (v1.0) |
| Multiple choice only for v1 | Focus on core loop working well before adding question variety | Shipped (v1.0) |
| Discriminated union question models | Future types without flat optional fields; see archived requirements | Shipped (v1.0) |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-04-27 — Phase 6 delivered; focus **phase 7** (per-question regeneration).*
