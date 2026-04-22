# AI Quiz Generator MVP

## What This Is

A web application that lets anyone generate multiple-choice quizzes from either a topic prompt or an uploaded document. The Python backend calls the OpenAI API to produce questions, and users can export the generated quiz. The app is publicly hosted with no login required — ship a link and anyone can try it.

## Core Value

Given a topic or document, produce a ready-to-use multiple-choice quiz in seconds — no account, no friction.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] User can enter a topic/prompt and generate a multiple-choice quiz
- [ ] User can upload a document (text/PDF) and generate questions from its content
- [ ] User can configure number of questions to generate
- [ ] AI generates well-formed multiple-choice questions (4 options, 1 correct answer)
- [ ] User can review generated questions and see correct answers
- [ ] User can select the AI model to use for generation (models sourced from openai-hk.com pricing)
- [ ] User can export/download the quiz (JSON and/or copy-to-clipboard)
- [ ] App is publicly accessible via a URL on Railway/Render with no login required

### Out of Scope

- User accounts / authentication — MVP is anonymous; saves complexity for v1
- True/False, short-answer, fill-in-the-blank questions — multiple choice only for MVP focus
- Quiz scoring / response collection — generation only, not proctoring
- Custom branding / themes — plain functional UI for MVP
- Question editing / regeneration of individual questions — export the batch, iterate via regenerate

## Context

- **Reference product**: Jotform AI Quiz Generator (https://www.jotform.com/ai/quiz-generator/) — the UX pattern to replicate at MVP scale
- **AI API**: OpenAI-compatible endpoint at https://www.openai-hk.com (drop-in for openai Python SDK)
- **Stack**: Python (FastAPI) backend + React (Vite) frontend, deployed on Railway (backend) + Vercel (frontend)
- **Target users**: Teachers, trainers, students, trivia enthusiasts — anyone who needs a quiz fast

## Constraints

- **Tech stack**: Python backend (FastAPI), React frontend — decided during initialization
- **AI provider**: openai-hk.com OpenAI-compatible API — backend calls this endpoint for question generation
- **Auth**: None — fully anonymous, no session management required
- **Deployment**: Must produce a publicly shareable URL; Railway (backend) + Vercel (frontend) chosen
- **MVP scope**: Multiple choice only, no persistence, no user management

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| FastAPI over Flask | Async, auto-docs, cleaner typed API, better for AI streaming | — Pending |
| React (Vite) over Next.js | Simpler deployment split; backend is pure API, frontend is pure UI | — Pending |
| No auth | MVP goal is demos and sharing; auth adds friction and time | — Pending |
| openai-hk.com API | Specified by user — drop-in OpenAI-compatible endpoint | — Pending |
| Multiple choice only for v1 | Focus on core loop working well before adding question variety | — Pending |

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
*Last updated: 2026-04-22 after initialization*
