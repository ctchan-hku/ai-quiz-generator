# AI Quiz Generator MVP

## Current state (milestone)

- **v1.0** — shipped & archived (tag `v1.0`): [.planning/milestones/v1.0-ROADMAP.md](milestones/v1.0-ROADMAP.md)
- **v1.1** — shipped & archived **2026-04-30** (tag `v1.1`): [.planning/milestones/v1.1-ROADMAP.md](milestones/v1.1-ROADMAP.md) · [.planning/milestones/v1.1-REQUIREMENTS.md](milestones/v1.1-REQUIREMENTS.md).
- **v1.2** — shipped & archived **2026-05-05** (tag `v1.2`): [.planning/milestones/v1.2-ROADMAP.md](milestones/v1.2-ROADMAP.md) · [.planning/milestones/v1.2-REQUIREMENTS.md](milestones/v1.2-REQUIREMENTS.md). Summary: [.planning/MILESTONES.md](MILESTONES.md).
- **v1.3** — **active** — layered system architecture (data → generation → review → deployment), aligned with [docs/system-flow](../docs/system-flow). Live roadmap: [.planning/ROADMAP.md](ROADMAP.md) · requirements: [.planning/REQUIREMENTS.md](REQUIREMENTS.md).

## Current Milestone: v1.3 Layered system architecture

**Goal:** Evolve the MVP toward the university-grade pipeline in [docs/system-flow](../docs/system-flow) by defining and implementing a **four-layer architecture** (data, generation, review, deployment) with clear module boundaries, contracts, and incremental vertical slices—without breaking anonymous, topic-first quiz generation.

**Target features:**

- **Data layer** — Content-unit model, index abstraction, and a minimal dev-time index so retrieval can attach to real structures before full doc ingestion ships.
- **Generation layer** — Optional structured generation spec, planning/retrieval hook before the LLM, and a sequential validator pipeline integrated with MCQ generation.
- **Review layer** — UI affordances for pipeline metadata (spec, validation outcome, placeholders for citations/rationales) and item disposition (approve / reject + reason) carried into export.
- **Deployment layer** — Publish-oriented export bundle and structured logging (or metrics hooks) across stages for operability and future LMS handoff.

**Reference:** [docs/system-flow](../docs/system-flow) (Phases 1–5 narrative and layered diagram).

## What This Is

A web application that lets anyone generate multiple-choice quizzes from a topic prompt (document upload planned for a future milestone). The Python backend calls an OpenAI-compatible API to produce questions; users refine per question, compare models by **price**, see **estimated USD cost** per run, and export the quiz. The app is publicly hosted with no login required.

## Core Value

Given a topic or document, produce a ready-to-use multiple-choice quiz in seconds — no account, no friction.

## Requirements

### Validated

- **Phase 1 (Backend Scaffold)** — FastAPI + CORS; `GET /health`, `GET /api/models`; gated `POST /api/debug/chat-completion`; Railway deploy with env-based config. *Validated 2026-04-22 (`01-UAT.md`).*
- **Phases 2–5 (v1 topic MVP)** — Topic generation, review, model selection, export: plain-text clipboard + JSON journal with optional per-question comments. *Shipped 2026-04-24.*
- **Phases 6–9 (v1.1)** — Few-shot + catalog; per-question regeneration + FE version stacks; `user_instructions`; reasoning-first prompts + post-parse shuffle. *Archived [v1.1-REQUIREMENTS.md](milestones/v1.1-REQUIREMENTS.md).*
- **Phases 10–11 (v1.2)** — **`GET /api/models`** pricing; **`cost_usd`** on quiz and question generate; **model board** + price sort; **Stop**/abort; cost on review, clipboard, journal (schema v2); backend **client-disconnect** cancellation. *Shipped 2026-05-05 — archived [v1.2-REQUIREMENTS.md](milestones/v1.2-REQUIREMENTS.md); UAT `10-UAT.md` / `11-UAT.md`.*

### Active

- [ ] App remains publicly accessible via Railway + Vercel with no login *(ongoing ops check)*

### Out of Scope

- Full LMS integration, live student attempts, and psychometric pipelines — future; v1.3 may only stub hooks and export shape  
- End-to-end secure item index and misconception library as in [docs/system-flow](../docs/system-flow) — v1.3 prepares contracts and stubs; full pipelines are later  
- Document upload — still a separate milestone after data contracts exist  
- User accounts / authentication — MVP anonymous  
- Non–multiple-choice question types in generator — MCQ focus  
- Quiz scoring / proctoring — generation only  
- Custom branding — functional UI first  
- Manual rich-text **editing** of question text — **AI refine** only (v1.1+)

## Context

- **Reference UX**: Jotform AI Quiz Generator (pattern at MVP scale).
- **AI API**: OpenAI-compatible endpoint (e.g. openai-hk.com) via official Python SDK.
- **Stack**: FastAPI (Railway) + React/Vite (Vercel).
- **Users**: Teachers, trainers, students, hobbyists.

## Constraints

- Python backend + React frontend — fixed stack for MVP.
- No auth — anonymous use.
- Deploy: shareable URLs on Railway + Vercel.
- Question schema: Pydantic/TS discriminated union; generator focuses on **`multiple_choice`**.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| FastAPI + React (Vite) | Split API/UI deploy | Shipped |
| No auth | Low friction demos | Shipped |
| Post-parse option shuffle | Remove positional bias | v1.1 |
| Model catalog merge (`AVAILABLE_MODELS` + reference JSON) | Allowlist + optional reference prices | v1.2 |
| **`cost_usd`** from usage × USD/M rates | Transparent spend estimate | v1.2 |
| Model **board** vs `<select>` | Price comparison UX | v1.2 |
| **AbortSignal** + server disconnect race | User Stop + less wasted backend work | v1.2 |

## Evolution

Updated at milestone **v1.3** start (2026-05-05): layered architecture milestone defined; **v1.2** remains validated below.

---
*Last updated: 2026-05-05 — **v1.3** milestone started (layered architecture).*
