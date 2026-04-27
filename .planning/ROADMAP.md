# Roadmap — AI Quiz Generator

**Active milestone:** **v1.1** — Generation quality & control *(few-shot examples, math model, per-question regeneration)*  
**Last updated:** 2026-04-27 (Phase 7 planned)  
**Prior release:** [v1.0 MVP (archived)](milestones/v1.0-ROADMAP.md)

---

## Phases

- [x] **Phase 6: Few-shot examples + math model** — Extend `POST /api/generate/text` with optional `few_shot_examples`; inject into system prompt in `llm.build_messages`; add **gpt-4.1** to default `AVAILABLE_MODELS`; QuizForm UI + API/types; README / `.env.example` (**MOD-01/02**, **AI-FS-01…04**, **FE-FS-01…03**, **DEPLOY-04**)
- [ ] **Phase 7: Per-question regeneration** — **`POST /api/generate/question`** (same pattern as `/api/generate/text`) with `topic`, **`question`** (current MCQ), optional **`comment`**; no sibling payload; **shared** 3/hour limit with generate; client **version stacks** + `<select>` + export from **selected** versions (**AI-RG-01…05**, **FE-RG-01…07**)

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

**Goal:** From review, user can **refine** one MCQ by sending the **current** `MultipleChoiceQuestion` + optional **Comment** to **`POST /api/generate/question`**; prior versions stay in a **client-side stack**; a **version control** picks the active revision for display, further refinement, and export.

**Depends on:** Phase 6 *(complete)*  

**Requirements:** AI-RG-01 … AI-RG-05, FE-RG-01 … FE-RG-07  

**Success criteria:**

1. **`POST /api/generate/question`** returns one validated `MultipleChoiceQuestion`; request body includes **`question`** (current MCQ) and optional **`comment`** (max 2_000) per **AI-RG-01**; no sibling payload.
2. Rate limit: **one** 3/hour IP bucket shared with `POST /api/generate/text` (documented).
3. UI **appends** a new version and selects it; user can switch versions; export/journal uses **selected** versions only.
4. Error paths do not destroy the quiz or version history.

**Plans:**

- [.planning/phases/07-regenerate-question/07-RESEARCH.md](phases/07-regenerate-question/07-RESEARCH.md)
- Wave 1 — Backend: [.planning/phases/07-regenerate-question/07-01-PLAN.md](phases/07-regenerate-question/07-01-PLAN.md)
- Wave 2 — Frontend: [.planning/phases/07-regenerate-question/07-02-PLAN.md](phases/07-regenerate-question/07-02-PLAN.md) *(depends on 07-01)*

**Context:** [.planning/phases/07-regenerate-question/07-CONTEXT.md](phases/07-regenerate-question/07-CONTEXT.md)

---

## Progress

| Phase | Status | Target |
|-------|--------|--------|
| 6. Few-shot + math model | Complete (2026-04-27) | v1.1 |
| 7. Per-question regeneration | Planned | v1.1 |

---

## Coverage

See [.planning/REQUIREMENTS.md](REQUIREMENTS.md) traceability table.
