# Roadmap — AI Quiz Generator

**Active milestone:** **v1.1** — Generation quality & control *(few-shot examples, math model, per-question regeneration)*  
**Last updated:** 2026-04-27 (Phase 6 complete)  
**Prior release:** [v1.0 MVP (archived)](milestones/v1.0-ROADMAP.md)

---

## Phases

- [x] **Phase 6: Few-shot examples + math model** — Extend `POST /api/generate/text` with optional `few_shot_examples`; inject into system prompt in `llm.build_messages`; add **gpt-4.1** to default `AVAILABLE_MODELS`; QuizForm UI + API/types; README / `.env.example` (**MOD-01/02**, **AI-FS-01…04**, **FE-FS-01…03**, **DEPLOY-04**)
- [ ] **Phase 7: Per-question regeneration** — `POST /api/generate/regenerate-question` with topic, full quiz, index, instruction; single-question LLM + parse retry + rate limit; QuizDisplay regenerate flow + state machine replace-at-index (**AI-RG-01…05**, **FE-RG-01…04**)

---

## Phase details

### Phase 6: Few-shot examples + math model

**Goal:** Users can optionally supply up to three example/style strings that are woven into the system prompt; the default model list includes a math-forward **gpt-4.1** option.

**Depends on:** v1.0 complete  
**Requirements:** MOD-01, MOD-02, AI-FS-01, AI-FS-02, AI-FS-03, AI-FS-04, FE-FS-01, FE-FS-02, FE-FS-03, DEPLOY-04  

**Success criteria:**

1. `GenerateTextRequest` accepts optional `few_shot_examples` with validation (max 3, max length per string).
2. Generated quizzes reflect user examples in tone/structure when provided (UAT spot-check documented).
3. `GET /api/models` lists gpt-4.1 with an appropriate label when using defaults or updated Railway JSON.
4. Frontend sends examples only on generate; no regression on topic-only generate.

**Plans:** [.planning/phases/06-few-shot-math-model/06-01-PLAN.md](phases/06-few-shot-math-model/06-01-PLAN.md) (backend + docs), [.planning/phases/06-few-shot-math-model/06-02-PLAN.md](phases/06-few-shot-math-model/06-02-PLAN.md) (frontend — add/remove example rows)

- Backend: extend Pydantic request model, `build_messages` / `generate_quiz` signature, wire parser `messages`
- Config: `_FALLBACK_MODELS` + `.env.example`
- Frontend: types, `generateQuiz` body, QuizForm optional examples (`<details>`, Add / Remove rows, max 3)

---

### Phase 7: Per-question regeneration

**Goal:** From review, user can regenerate one MCQ with an optional instruction; the rest of the quiz is unchanged.

**Depends on:** Phase 6 *(can technically parallel if API contracts frozen — prefer sequential to reuse prompt patterns)*  

**Requirements:** AI-RG-01 … AI-RG-05, FE-RG-01 … FE-RG-04  

**Success criteria:**

1. New endpoint returns one validated `MultipleChoiceQuestion` for a valid index.
2. Rate limit behaviour documented and consistent with full-quiz generate.
3. UI replaces exactly one question; export/journal sees updated content.
4. Error paths do not destroy the existing quiz.

**Plans:** (to be written in `/gsd-plan-phase 7`)

- Backend: router, Pydantic models, `llm` helper for single-question messages, reuse/adapt parser retry
- Frontend: API client, `useQuizMachine` action `REPLACE_QUESTION` (or equivalent), QuizDisplay UX

---

## Progress

| Phase | Status | Target |
|-------|--------|--------|
| 6. Few-shot + math model | Complete (2026-04-27) | v1.1 |
| 7. Per-question regeneration | Planned | v1.1 |

---

## Coverage

See [.planning/REQUIREMENTS.md](REQUIREMENTS.md) traceability table.
